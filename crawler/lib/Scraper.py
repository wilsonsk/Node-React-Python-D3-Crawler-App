"""
Filename: Scraper.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Class responsible for scraping HTML pages and returning
             keyword, title, and URL link results.
"""

import pprint, re
# BEAUTIFUL SOUP
from bs4 import BeautifulSoup
# REQUESTS
import requests
# UTILS
from utils.request_utils import request_page_crawl
# CONSTANTS
from constants import CRAWLER_MAX_TIMEOUT

class Scraper:

	def __init__(self, url=None):
		if url is None:
			raise TypeError('url must not be NoneType')
		if not isinstance(url, unicode):
			raise TypeError('url must be a Unicode string')
		self.url = url

	def scrape_url(self, keyword):		
		"""try:
			headers = get_request_headers()
			res = requests.get(self.url, headers=headers, timeout=CRAWLER_MAX_TIMEOUT)
		except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
			raise requests.exceptions.HTTPError('Request failed. Moving to next queue item.')
		"""
		# Attempt to acquire the response object. Throws CrawlerRequestException on failure.
		res = request_page_crawl(self.url, robots_request=False)

		# Acquire the parsed document tree
		document = BeautifulSoup(res.content, 'lxml') #html5lib

		# Find links in the document
		url_list = self._find_all_links(document)

		# Find document title if it exists, None otherwise.
		title = self._get_title(document)

		# Keyword search
		keyword_found = False
		if keyword is not None:
			keyword_found = self._check_keyword(document, keyword)

		return url_list, title, keyword_found, res.url

	def _find_all_links(self, document):
		url_list = []
		for tag in document.find_all('a'):
			url_result = self._get_url(tag)
			if url_result is not None:
				url_list.append(self._get_url(tag))
		return url_list

	def _get_url(self, tag):
		tag = unicode(tag)
		# validate the tag prior to retrieving url indices.
		if not self._validate_tag(tag):
			return None
		# Retrieve url indices and form the candidate url.
		quote_start = tag.find('"', tag.find('href'))
		quote_end = tag.find('"', quote_start + 1)
		candidate_url = tag[quote_start + 1: quote_end]
		# Validate the candidate url.
		if not self._validate_candidate_url(candidate_url):
			return None
		return tag[quote_start + 1: quote_end]

	def _validate_tag(self, tag):
		# If we encounter 'javascript:void(0)', return None.
		if tag.find(u'javascript:void(0)') != -1:
			return False
		# If the anchor tag doesn't contain an href, return None.
		if tag.find(u'href') == -1:
			return False
		return True

	def _validate_candidate_url(self, candidate_url):
		# If we encounter an unaccompanied relative fragment, return None.
		if candidate_url.find(u'#') == 0:
			return False
		return True

	def _get_title(self, document):
		try:
			title = document.title.string
		except AttributeError as e:
			title = None
		if title is not None:
			title = title.strip().replace('\\\n', '')
		return title

	def _check_keyword(self, document, keyword):
		regex = re.compile(re.escape(keyword), re.IGNORECASE)
		# Search string contents
		if len(document.find_all(string=regex, limit=1)) > 0:
			return True
		# Search tag names
		if len(document.find_all(regex, limit=1)) > 0:
			return True
		# Search tag ids
		if len(document.find_all(id=regex, limit=1)) > 0:
			return True
		if len(document.find_all(class_=regex, limit=1)) > 0:
			return True
		return False