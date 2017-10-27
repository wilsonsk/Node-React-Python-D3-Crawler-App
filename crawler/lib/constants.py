"""
Filename: constants.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: File containing global crawler constants.
"""

import sys

# Crawler constants
CRAWLER_USER_AGENT = 'Andromeda_Crawler'  # Crawler user-agent string for submission with requests
CRAWLER_MAX_TIMEOUT = 4.55				  # Crawler maximum timeout (in seconds). Slightly larger than 1.5x the TCP retransmission window.

# Command line argument constants
CL_MAX_TREE_DEPTH = 5					  # Maximum tree depth for breadth-first search
CL_MIN_TREE_DEPTH = 0					  # Minimum tree depth for breadth-first search

CL_MAX_PAGE_LIMIT = 1000				  # Maximum number of pages to crawl
CL_MIN_PAGE_LIMIT = 0					  # Minimum number of pages to crawl
CL_DEFAULT_PAGE_LIMIT = 10				  # Default number of pages to crawl

# Robots.txt record constants
RECORD_STALE_SECONDS = 2 * 604800         # Time in seconds before a record must be updated
RECORD_MAX_BYTES = 500 * 1024             # Maximum bytes to be processed in a robots.txt file
RECORD_MAX_REDIRECTS = 5                  # Maximum allowed redirects in searching for a robots.txt file
RECORD_MAX_LEN = 512					  # Maximum character length of a single record

# Debug constants
DEBUG_LOG_MODE = False					  # Set to true for STDERR output. False to hide log messsages.

# System constants
SYS_STDOUT_ENCODING = sys.stdout.encoding # System STDOUT encoding settings
if SYS_STDOUT_ENCODING is None:
	SYS_STDOUT_ENCODING = 'utf-8'

# Exit status constants
EXIT_STATUS_OK = 0						  # Exit status for successful crawl
EXIT_STATUS_INVALID_ARGS = 1			  # Exit status for invalid argument(s) to crawler
EXIT_STATUS_INVALID_STARTING_URL = 2	  # Exit status for invalid starting URL
EXIT_STATUS_INVALID_READ = 3			  # Exit status for errors in reading the output file