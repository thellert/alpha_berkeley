#!/usr/bin/env python3
"""
Primary documentation launcher - build and serve documentation with cache management

This script cleans build cache, builds documentation, and serves it in detached mode.
With --with-act, it uses GitHub Actions (act) to build in the same environment as CI.
"""

import os
import sys
import subprocess
import time
import signal
import threading
import atexit
import socket
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

class DetachedDocServer:
    def __init__(self, port=8081, docs_dir=None):
        self.port = port
        self.server = None
        self.docs_dir = docs_dir or Path.cwd()
        self.pid_file = self.docs_dir / f"docs_server_{port}.pid"

    def is_port_in_use(self, port):
        """Check if a port is currently in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return False
            except OSError:
                return True



    def kill_process_on_port(self, port):
        """Try to kill any process using the specified port (Linux/Mac) with multiple approaches."""
        killed_any = False

        # Method 1: Use lsof (most reliable)
        pids_found = self._find_pids_with_lsof(port)

        # Method 2: Use netstat if lsof didn't work
        if not pids_found:
            pids_found = self._find_pids_with_netstat(port)

        # Method 3: Use ss command if available
        if not pids_found:
            pids_found = self._find_pids_with_ss(port)

        if not pids_found:
            print(f"No processes found using port {port}")
            return False

        print(f"Found {len(pids_found)} process(es) using port {port}: {pids_found}")

        # Try to kill each process
        for pid in pids_found:
            if self._kill_process_gracefully(pid):
                killed_any = True

        if killed_any:
            # Wait for port to be freed
            print(f"Waiting for port {port} to be freed...")
            for i in range(10):  # Wait up to 10 seconds
                time.sleep(1)
                if not self.is_port_in_use(port):
                    print(f"Port {port} is now free")
                    return True
                print(f"   Still waiting... ({i+1}/10)")

        # Final check - if port is still in use, try one more aggressive round
        if self.is_port_in_use(port):
            print(f"Port {port} still in use, trying more aggressive approach...")
            remaining_pids = self._find_pids_with_lsof(port)
            for pid in remaining_pids:
                try:
                    print(f"Force killing process {pid} with SIGKILL")
                    os.kill(int(pid), signal.SIGKILL)
                    time.sleep(0.5)
                except (OSError, ValueError) as e:
                    print(f"   Failed to kill {pid}: {e}")

            # Final wait
            time.sleep(2)
            if not self.is_port_in_use(port):
                print(f"Port {port} is now free after aggressive kill")
                return True

        return not self.is_port_in_use(port)

    def _find_pids_with_lsof(self, port):
        """Find PIDs using lsof command."""
        try:
            result = subprocess.run(['lsof', '-t', f'-i:{port}'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                pids = [pid.strip() for pid in result.stdout.strip().split('\n') if pid.strip()]
                return [pid for pid in pids if pid.isdigit()]
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            pass
        return []

    def _find_pids_with_netstat(self, port):
        """Find PIDs using netstat command."""
        try:
            result = subprocess.run(['netstat', '-tlnp'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                pids = []
                for line in result.stdout.split('\n'):
                    if f':{port} ' in line or f':{port}\t' in line:
                        parts = line.split()
                        for part in parts:
                            if '/' in part:
                                pid_part = part.split('/')[0]
                                if pid_part.isdigit():
                                    pids.append(pid_part)
                return pids
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            pass
        return []

    def _find_pids_with_ss(self, port):
        """Find PIDs using ss command."""
        try:
            result = subprocess.run(['ss', '-tlnp', f'sport = :{port}'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                pids = []
                for line in result.stdout.split('\n'):
                    if 'pid=' in line:
                        # Extract PID from ss output format like users:(("python3",pid=12345,fd=3))
                        import re
                        pid_match = re.search(r'pid=(\d+)', line)
                        if pid_match:
                            pids.append(pid_match.group(1))
                return pids
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            pass
        return []

    def _kill_process_gracefully(self, pid):
        """Kill a process gracefully (SIGTERM first, then SIGKILL if needed)."""
        try:
            pid_int = int(pid)
            print(f"Attempting to kill process {pid} gracefully...")

            # Check if process exists first
            try:
                os.kill(pid_int, 0)
            except OSError:
                print(f"   Process {pid} already dead")
                return True

            # Try SIGTERM first
            os.kill(pid_int, signal.SIGTERM)

            # Wait up to 5 seconds for graceful termination
            for i in range(5):
                time.sleep(1)
                try:
                    os.kill(pid_int, 0)  # Check if process still exists
                except OSError:
                    print(f"   Process {pid} terminated gracefully")
                    return True

            # If still running, try SIGKILL
            print(f"   Process {pid} didn't respond to SIGTERM, trying SIGKILL...")
            try:
                os.kill(pid_int, signal.SIGKILL)
                time.sleep(1)

                # Verify it's dead
                try:
                    os.kill(pid_int, 0)
                    print(f"   Process {pid} still running after SIGKILL")
                    return False
                except OSError:
                    print(f"   Process {pid} killed with SIGKILL")
                    return True

            except OSError as e:
                print(f"   Failed to kill process {pid}: {e}")
                return False

        except (ValueError, OSError) as e:
            print(f"   Error killing process {pid}: {e}")
            return False

    def clean_docs(self):
        """Clean the documentation build cache using make clean."""
        print("Cleaning documentation build cache...")
        try:
            result = subprocess.run(['make', 'clean'], 
                                 capture_output=True, 
                                 text=True, 
                                 check=True)
            print("Documentation cache cleaned successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error cleaning documentation cache: {e}")
            print(f"   Error output: {e.stderr}")
            return False

    def build_docs(self, clean_first=True):
        """Build the documentation using make html."""
        if clean_first:
            if not self.clean_docs():
                return False

        print("Building documentation...")
        try:
            result = subprocess.run(['make', 'html'], 
                                 capture_output=True, 
                                 text=True, 
                                 check=True)
            print("Documentation built successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error building documentation: {e}")
            print(f"   Error output: {e.stderr}")
            return False

    def build_with_act(self):
        """Build documentation using GitHub Actions (act) for environment matching."""
        print("Building documentation with GitHub Actions (act)...")
        print("This tests the same environment as the remote GitHub build.")

        # Check if act is available
        try:
            subprocess.run(['act', '--version'], 
                         capture_output=True, 
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Error: 'act' is not installed or not found in PATH")
            print("   Install act to use this feature:")
            print("   - macOS/Linux: brew install act")
            print("   - Windows: Download from https://github.com/nektos/act/releases")
            return False

        # Change to project root (parent of docs directory)
        project_root = self.docs_dir.parent
        original_cwd = Path.cwd()
        os.chdir(project_root)

        try:
            print("Running: act -j build")
            print("(This may take a while on first run as Docker images are downloaded)")

            # Run act to build the documentation
            result = subprocess.run(['act', '-j', 'build'], 
                                 text=True, 
                                 check=True)

            print("✅ Documentation built successfully with act!")
            print("   Build matches GitHub Actions environment")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Error building documentation with act: {e}")
            print("   This indicates the build would also fail on GitHub")
            return False
        except KeyboardInterrupt:
            print("\n⚠️  Build interrupted by user")
            return False
        finally:
            # Always return to original directory
            os.chdir(original_cwd)

    def is_running(self):
        """Check if server is already running."""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process is still running
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            # Process doesn't exist or pid file is corrupted
            self.pid_file.unlink(missing_ok=True)
            return False

    def stop_existing_server(self):
        """Stop existing server if running."""
        if not self.pid_file.exists():
            return True

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            print(f"Stopping existing server (PID: {pid})...")
            os.kill(pid, signal.SIGTERM)

            # Wait for process to terminate
            for _ in range(10):  # Wait up to 10 seconds
                try:
                    os.kill(pid, 0)
                    time.sleep(1)
                except OSError:
                    break

            self.pid_file.unlink(missing_ok=True)
            print("Existing server stopped")
            return True

        except (OSError, ValueError) as e:
            print(f"Error stopping existing server: {e}")
            self.pid_file.unlink(missing_ok=True)
            return True

    def start_detached(self):
        """Start the server in detached mode."""
        build_dir = Path("build/html")

        if not build_dir.exists():
            print(f"Build directory {build_dir} does not exist!")
            return False

        # Double-check port is available before forking
        if self.is_port_in_use(self.port):
            print(f"Port {self.port} is still in use! Cannot start server.")
            return False

        # Fork the process to run in background
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process - wait a moment to see if child starts successfully
                time.sleep(1)

                # Check if child is still running and port is now in use
                try:
                    os.kill(pid, 0)  # Check if process exists
                    if self.is_port_in_use(self.port):
                        print(f"Documentation server started in background!")
                        print(f"View your documentation at: http://localhost:{self.port}")
                        print(f"Or try: http://127.0.0.1:{self.port}")
                        print(f"Server PID: {pid}")
                        print(f"To stop: python launch_docs.py --stop")
                        return True
                    else:
                        print(f"Server failed to start on port {self.port}")
                        return False
                except OSError:
                    print("Server process failed to start")
                    return False
        except OSError:
            print("Failed to fork process")
            return False

        # Child process - run the server
        try:
            # Create new session
            os.setsid()

            # Change to build directory
            os.chdir(build_dir)

            # Save PID (use absolute path since we changed directories)
            pid_file_abs = self.docs_dir / f"docs_server_{self.port}.pid"
            with open(pid_file_abs, 'w') as f:
                f.write(str(os.getpid()))

            # Register cleanup function
            atexit.register(self.cleanup)

            # Start server
            handler = SimpleHTTPRequestHandler
            self.server = HTTPServer(("", self.port), handler)

            # Serve forever
            self.server.serve_forever()

        except Exception as e:
            # Child process error - write to a log file since stdout might not be visible
            error_log = self.docs_dir / "server_error.log"
            with open(error_log, 'w') as f:
                f.write(f"Server error: {e}\n")
            sys.exit(1)

        return True

    def cleanup(self):
        """Cleanup function called on exit."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        self.pid_file.unlink(missing_ok=True)

def find_docs_directory():
    """Find the docs directory by looking in common locations."""
    current_dir = Path.cwd()

    # Check if we're already in docs directory
    if (current_dir / "source").exists() and (current_dir / "Makefile").exists():
        return current_dir

    # Check if docs directory exists in current directory
    docs_dir = current_dir / "docs"
    if docs_dir.exists() and (docs_dir / "source").exists() and (docs_dir / "Makefile").exists():
        return docs_dir

    # Check parent directory for docs
    parent_docs = current_dir.parent / "docs"
    if parent_docs.exists() and (parent_docs / "source").exists() and (parent_docs / "Makefile").exists():
        return parent_docs

    # Search up the directory tree
    for parent in current_dir.parents:
        docs_candidate = parent / "docs"
        if docs_candidate.exists() and (docs_candidate / "source").exists() and (docs_candidate / "Makefile").exists():
            return docs_candidate

    return None

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Primary documentation launcher - build and serve with cache management")
    parser.add_argument("--port", "-p", type=int, default=8082, 
                       help="Port to serve on (default: 8082)")
    parser.add_argument("--stop", action="store_true",
                       help="Stop the running server")
    parser.add_argument("--status", action="store_true",
                       help="Check if server is running")
    parser.add_argument("--build-only", action="store_true",
                       help="Only build documentation, don't serve")
    parser.add_argument("--no-clean", action="store_true",
                       help="Skip cleaning build cache before building")
    parser.add_argument("--clean-only", action="store_true",
                       help="Only clean the build cache, don't build or serve")
    parser.add_argument("--docs-dir", type=str,
                       help="Path to documentation directory (auto-detected if not specified)")
    parser.add_argument("--with-act", action="store_true",
                       help="Build with GitHub Actions (act) first, then serve locally")


    args = parser.parse_args()

    # Find or use specified docs directory
    if args.docs_dir:
        docs_dir = Path(args.docs_dir).resolve()
        if not docs_dir.exists():
            print(f"Specified docs directory does not exist: {docs_dir}")
            return 1
    else:
        docs_dir = find_docs_directory()

    if not docs_dir:
        print("Could not find docs directory!")
        print("Please ensure you're in the project directory or specify --docs-dir")
        print("Looking for a directory with 'source' folder and 'Makefile'")
        return 1

    print(f"Using docs directory: {docs_dir}")

    # Change to docs directory
    original_cwd = Path.cwd()
    os.chdir(docs_dir)

    server = DetachedDocServer(port=args.port, docs_dir=docs_dir)

    if args.stop:
        if server.is_running():
            server.stop_existing_server()
        else:
            print("Server is not running")
        return 0

    if args.status:
        if server.is_running():
            print(f"Server is running on port {args.port}")
            print(f"View at: http://localhost:{args.port}")
        else:
            print("Server is not running")
        return 0

    if args.clean_only:
        print("Cleaning documentation cache only...")
        success = server.clean_docs()
        return 0 if success else 1

    if args.build_only:
        print("Building documentation only...")
        clean_first = not args.no_clean
        success = server.build_docs(clean_first=clean_first)
        return 0 if success else 1

    # Handle any existing processes on the port
    if server.is_running():
        print(f"Stopping existing documentation server...")
        server.stop_existing_server()
        time.sleep(2)  # Give it time to fully stop

    # Kill any other processes using the port
    if server.is_port_in_use(args.port):
        print(f"Port {args.port} is in use, killing existing process...")
        if server.kill_process_on_port(args.port):
            print("Freed port")
            time.sleep(2)  # Give it time to release the port
        else:
            print(f"Could not automatically free port {args.port}")
            print("You may need to manually stop the process using this port")

    # Build documentation
    if args.with_act:
        # Build with act (GitHub Actions environment)
        if not server.build_with_act():
            return 1
    else:
        # Regular build with make
        clean_first = not args.no_clean
        if not server.build_docs(clean_first=clean_first):
            return 1

    # Start detached server
    server.start_detached()
    return 0

if __name__ == "__main__":
    sys.exit(main()) 