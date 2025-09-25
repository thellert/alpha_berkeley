#!/usr/bin/env python3
"""
Simple systematic PV scraper using nested loops.

This script systematically discovers all PVs by:
1. Going through every character: a-z, A-Z, 0-9, '-', '_', ':', '.'
2. Searching with pattern 'X*' for each character X
3. If max results are returned, recursively expand with 'XX*', 'XY*', etc.
4. Continue until all queries return less than max results
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set
from channel_finder import search_channel_finder

class SystematicPVScraper:
    def __init__(self, output_dir: str = "pv_data_systematic", delay: float = 0.2):
        """
        Initialize the systematic PV scraper.
        
        Args:
            output_dir: Directory to save output files
            delay: Delay between requests (seconds)
        """
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.all_pvs = []
        self.pv_names = set()
        self.max_results_per_query = 10000
        self.queries_made = 0
        
        # All characters to explore systematically
        self.chars = (
            list('abcdefghijklmnopqrstuvwxyz') +  # a-z
            list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') +  # A-Z  
            list('0123456789') +                  # 0-9
            ['-', '_', ':', '.']                  # delimiters
        )
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.log_file = self.output_dir / f"scrape_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
    def log(self, message: str):
        """Log message to both console and file."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + '\n')
    
    def query_pattern(self, pattern: str) -> List[Dict]:
        """Query the channel finder with a pattern."""
        try:
            result = search_channel_finder(
                name_pattern=pattern, 
                max_results=self.max_results_per_query,
                verbose=False
            )
            data = json.loads(result)
            
            self.queries_made += 1
            
            if 'error' in data:
                self.log(f"Error querying '{pattern}': {data['error']}")
                return []
            
            return data
            
        except Exception as e:
            self.log(f"Exception querying '{pattern}': {e}")
            return []
    
    def explore_prefix(self, prefix: str, max_depth: int = 8) -> int:
        """
        Explore a prefix systematically.
        
        Args:
            prefix: Current prefix to explore
            max_depth: Maximum recursion depth
            
        Returns:
            Number of new PVs found
        """
        if len(prefix) > max_depth:
            return 0
            
        # Search with current prefix
        pattern = f"{prefix}*"
        self.log(f"Searching: {pattern}")
        
        pvs = self.query_pattern(pattern)
        total_found = len(pvs)
        
        new_pvs_count = 0
        
        if total_found < self.max_results_per_query:
            # We got all PVs for this pattern, safe to add them
            for pv in pvs:
                pv_name = pv.get('name', '')
                if pv_name and pv_name not in self.pv_names:
                    self.all_pvs.append(pv)
                    self.pv_names.add(pv_name)
                    new_pvs_count += 1
            
            self.log(f"Pattern '{pattern}': {total_found} results (complete set), {new_pvs_count} new, Total unique: {len(self.all_pvs)}")
        
        else:
            # Hit max results, there might be more PVs - recurse deeper without adding
            self.log(f"Pattern '{pattern}': {total_found} results (hit max), recursing deeper...")
            
            # Try all possible next characters
            for char in self.chars:
                new_prefix = prefix + char
                new_pvs_count += self.explore_prefix(new_prefix, max_depth)
        
        return new_pvs_count
    
    def run_systematic_scrape(self, max_depth: int = 6):
        """
        Run the systematic scraping process.
        
        Args:
            max_depth: Maximum prefix depth to explore
        """
        self.log("Starting systematic PV scraping...")
        self.log(f"Characters to explore: {len(self.chars)}")
        self.log(f"Max results per query: {self.max_results_per_query}")
        self.log(f"Max depth: {max_depth}")
        
        start_time = time.time()
        
        try:
            # Go through each character systematically
            for i, char in enumerate(self.chars):
                self.log(f"\n=== Exploring character {i+1}/{len(self.chars)}: '{char}' ===")
                
                self.explore_prefix(char, max_depth)
                
                # Save progress periodically
                if (i + 1) % 20 == 0:
                    self.save_results()
                
                time.sleep(self.delay)
            
            # Final save
            files = self.save_results()
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.log(f"\nScraping completed in {duration:.2f} seconds")
            self.log(f"Total unique PVs found: {len(self.all_pvs)}")
            self.log(f"Total queries made: {self.queries_made}")
            
            return files
            
        except KeyboardInterrupt:
            self.log("Scraping interrupted by user")
            self.save_results()
            return None
        except Exception as e:
            self.log(f"Error during scraping: {str(e)}")
            self.save_results()
            raise

    def save_results(self):
        """Save current results."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.log(f"Saving results for {len(self.all_pvs)} PVs...")
        
        # Save complete JSON data
        json_file = self.output_dir / f"all_pvs_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(self.all_pvs, f, indent=2)
        
        # Save PV names list
        names_file = self.output_dir / f"pv_names_{timestamp}.txt"
        with open(names_file, 'w') as f:
            for name in sorted(self.pv_names):
                f.write(name + '\n')
        
        self.log(f"Saved to {json_file} and {names_file}")
        
        return {
            'json_file': str(json_file),
            'names_file': str(names_file)
        }

def main():
    """Main function to run the systematic scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple systematic PV scraper')
    parser.add_argument('--output-dir', default='pv_data_systematic', 
                       help='Output directory for results')
    parser.add_argument('--delay', type=float, default=0.2, 
                       help='Delay between requests (seconds)')
    parser.add_argument('--max-depth', type=int, default=6,
                       help='Maximum prefix depth to explore')
    
    args = parser.parse_args()
    
    scraper = SystematicPVScraper(
        output_dir=args.output_dir,
        delay=args.delay
    )
    
    try:
        files = scraper.run_systematic_scrape(max_depth=args.max_depth)
        if files:
            print(f"\nScraping successful! Check: {args.output_dir}")
        else:
            print("\nScraping was interrupted.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 