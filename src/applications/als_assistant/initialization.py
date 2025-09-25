"""
ALS Assistant Application Initialization Functions

This module contains all initialization functions specific to the ALS Assistant application.
These functions are called during pipeline startup based on the configuration.
"""

import logging
import subprocess
import nltk
from applications.als_assistant.services.pv_finder.util import initialize_nltk_resources

logger = logging.getLogger("framework_pipeline.als_assistant.initialization")


def setup_nltk_resources():
    """ALS Assistant specific NLTK resource setup."""
    logger.info("Setting up NLTK resources...")
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('stopwords', quiet=True)
        logger.info("NLTK resources setup complete.")
    except ImportError as e:
        logger.warning(f"Failed to import nltk: {e}")
    except Exception as e:
        logger.warning(f"Failed to setup NLTK resources: {e}")


def setup_system_packages():
    """ALS Assistant specific system package installation."""
    logger.info("Setting up system packages...")
    install_command = "apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*"
    try:
        process = subprocess.run(install_command, shell=True, check=True, capture_output=True, text=True)
        logger.info("iputils-ping installation completed.")
        logger.info(f"STDOUT: {process.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install iputils-ping: {e.stderr}")
    except FileNotFoundError:
        logger.warning("apt-get not found, skipping iputils-ping installation. This is expected if not in a Debian-based Docker container.")
    except Exception as e:
        logger.warning(f"Failed to setup system packages: {e}")


def setup_pv_finder_resources():
    """ALS Assistant specific PV Finder resource initialization."""
    logger.info("Initializing PV Finder resources...")
    try:
        initialize_nltk_resources()
        logger.info("PV Finder resources initialized.")
    except ImportError as e:
        logger.warning(f"Failed to import PV Finder utilities: {e}")
    except Exception as e:
        logger.warning(f"Failed to setup PV Finder resources: {e}") 