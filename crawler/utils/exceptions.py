"""
Filename: exceptions.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Custom crawler exceptions.
"""

class Error(Exception):
	"""Base class for other exceptions"""
	pass

class CrawlerRequestException(Error):
	"""Raised when a crawler request fails to produce a result object"""
	pass