"""
Filename: utils.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Error print utility functions.
"""
# Future
from __future__ import print_function
# Constants
from lib.constants import DEBUG_LOG_MODE
# Sys
import sys
# Requests
import requests

def errprint(*args, **kwargs):
	if DEBUG_LOG_MODE:
		print(*args, file = sys.stderr, **kwargs)

def erroutput(*args, **kwargs):
	print(*args, file = sys.stderr, **kwargs)