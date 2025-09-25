from typing import List, Dict, Any, Set, Optional
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize as nltk_word_tokenize
import random
from applications.als_assistant.services.pv_finder.examples_loader import example_loader

# Use global logger
from configs.logger import get_logger


def case_insensitive_eq(str1: str, str2: str) -> bool:
    """Case insensitive string equality check."""
    if not isinstance(str1, str) or not isinstance(str2, str):
        return str1 == str2
    return str1.lower() == str2.lower()


def case_insensitive_in(item: str, collection: List[str]) -> bool:
    """Case insensitive version of 'in' operator for strings."""
    if not isinstance(item, str):
        return item in collection
    return item.lower() in [s.lower() for s in collection if isinstance(s, str)]




def initialize_nltk_resources():
    """
    Initializes NLTK resources (stemmer, lemmatizer, tokenizer and downloads if necessary).
    This function should be called once at application startup.
    """
    global STEMMER, LEMMATIZER, word_tokenize

    logger = get_logger("framework", "base")

    # Assign to global for use in other functions
    word_tokenize = nltk_word_tokenize

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        logger.info("NLTK 'punkt' not found. Downloading...")
        nltk.download('punkt', quiet=False)
        logger.info("'punkt' downloaded.")
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        logger.info("NLTK 'wordnet' not found. Downloading...")
        nltk.download('wordnet', quiet=False)
        logger.info("'wordnet' downloaded.")
    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        logger.info("NLTK 'omw-1.4' not found. Downloading...")
        nltk.download('omw-1.4', quiet=False)
        logger.info("'omw-1.4' downloaded.")

    STEMMER = PorterStemmer()
    LEMMATIZER = WordNetLemmatizer()
    
    # Prime all NLTK components by calling them once to load their resources
    try:
        logger.info("Priming NLTK components...")
        word_tokenize("prime tokenizer") 
        STEMMER.stem("priming stemmer")
        LEMMATIZER.lemmatize("priming_lemmatizer", pos='n') # 'n' for noun, common use
        logger.info("NLTK Stemmer, Lemmatizer, and Tokenizer initialized and primed.")
    except Exception as e:
        logger.warning(f"Error priming NLTK components: {e}")
        # Proceeding with initialization even if priming fails for some reason
        logger.info("NLTK components initialized (priming may have failed for some components).")




def normalize_keywords(keywords: List[str]) -> Set[str]:
    """
    Normalize keywords using stemming and lemmatization to handle variations.
    For example, 'gaps' would match 'gap', 'running' would match 'run', etc.
    
    Args:
        keywords: List of keywords to normalize
        
    Returns:
        Set of normalized keywords, including both original and stemmed/lemmatized forms
    """
 
    normalized = set(keywords)  # Start with original keywords
       
    # Process each keyword
    for keyword in keywords:
        # Handle multi-word keywords
        words = word_tokenize(keyword.lower())
        
        # Add stemmed and lemmatized forms
        for word in words:
            # Add stemmed form
            stemmed = STEMMER.stem(word)
            if stemmed != word:
                normalized.add(stemmed)
                
            # Add lemmatized form (as noun)
            lemmatized = LEMMATIZER.lemmatize(word, pos='n')
            if lemmatized != word:
                normalized.add(lemmatized)
    
    return normalized



def get_examples_from_keywords(systems: List[str] = None, keywords: List[str] = None, num_examples: int = 20):
    """
    Get examples from keywords and systems using the type-safe example system
    
    Args:
        systems: List of identified systems relevant to the query
        keywords: List of keywords to match
        num_examples: Maximum number of examples to return
        
    Returns:
        List of PVFinderToolExample objects
    """

    
    # Use global logger
    logger = get_logger("als_assistant", "pv_finder")
    
    if not keywords:
        keywords = []
    if not systems:
        systems = []
    
    # Get all PV finder examples
    all_examples = example_loader.get_all_pv_examples()
    logger.info(f"Total examples loaded: {len(all_examples)}")
    
    # Get statistics to see what's available
    stats = example_loader.get_statistics()
    logger.info(f"Example statistics: {stats}")
    
    # Filter examples that match any system and any keyword
    matching_examples = []
    for example in all_examples:
        # Check if example matches any system
        system_match = not systems or any(example.matches_system(sys) for sys in systems)
        # Check if example matches any keyword
        keyword_match = not keywords or any(example.has_keyword(kw) for kw in keywords)
        
        # Special handling for general examples: they should match if system matches, regardless of keywords
        is_general_example = example.system == "general"
        
        # Special handling for fallback examples: they should match if system matches, regardless of keywords
        is_fallback_example = example.query_type == "fallback"
        
        # Add example if:
        # 1. It matches both system and keyword (normal case), OR
        # 2. It's a general example and matches the system (general fallback), OR
        # 3. It's a fallback example and matches the system (system-specific fallback)
        if (system_match and keyword_match) or (is_general_example and system_match) or (is_fallback_example and system_match):
            matching_examples.append(example)
            if system_match and keyword_match:
                match_reason = "system+keyword"
            elif is_general_example:
                match_reason = "general_fallback"
            else:
                match_reason = "system_fallback"
            logger.debug(f"Matched example ({match_reason}): system={example.system}, keywords={example.keywords}, query='{example.query}'")
    
    logger.info(f"Found {len(matching_examples)} matching examples for systems={systems}, keywords={keywords}")
    
    # Randomize the order of matching examples
    random.shuffle(matching_examples)
    
    # Limit to num_examples
    return matching_examples[:num_examples]




def format_pv_results_for_span(pv_results) -> str:
    """
    Format the PV results into a string.
    """
    all_pvs_for_span: List[str] = []
    if pv_results:
        for result_item in pv_results:
            if result_item and result_item.pvs:
                all_pvs_for_span.extend(result_item.pvs)
    return str(all_pvs_for_span) if all_pvs_for_span else "[ERR]: No PVs found"