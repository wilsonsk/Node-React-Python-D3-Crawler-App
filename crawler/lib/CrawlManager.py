"""
Filename: CrawlManager.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Class responsible for getting and setting link records in the database
             as well as preventing cycles with a dictionary of visited links.
"""

# CONSTANTS
from constants import RECORD_STALE_SECONDS
# BUILTINS
from datetime import datetime
import pprint
# LIB
from dbManager import dbManager
from UrlQueue import UrlQueue



class CrawlManager(dbManager):
	def __init__(self, config):
		self.queue = UrlQueue()
		self.count = 0
		self.visited = {}
		self.cooldown = {}

	def get_links(self, url):
		return self.conn_wrap(self._get_links, url)

	def _get_links(self, url):
		url = url[0]
		db = self.client.crawler_db
		links = db.links

		children = []
		document = links.find_one({'parent' : url})
		if document is not None and 'children' in document and 'title' in document:
			children.extend(document['children'])
			#children = children if len(children) > 0 else None
			title = document['title']
			return children, title
		return None, None

	def set_links(self, parent_url, child_urls, parent_title):
		self.conn_wrap(self._set_links, parent_url, child_urls, parent_title)

	def _set_links(self, args):
		parent_url = args[0]
		child_urls = args[1]
		parent_title = args[2]

		db = self.client.crawler_db
		links = db.links

		for child in child_urls:
			links.find_one_and_update(
				{ 'parent' : parent_url },
				{ '$push' : { 'children' : child } },
				upsert=True)

		if len(child_urls) <= 0:
			links.find_one_and_update(
				{ 'parent' : parent_url },
				{ '$set' : { 'children' : [] } },
				upsert=True)

		links.find_one_and_update(
			{ 'parent' : parent_url },
			{ '$set' : { 'title' : parent_title, 'timestamp' : datetime.utcnow() } } )

	def emplace_visited(self, url_str_with_scheme):
		if not self.visited_contains(url_str_with_scheme):
			# Strip the scheme from the url string
			url_str_no_scheme = self._strip_scheme(url_str_with_scheme)

			# Strip off a right forward slash if it's present
			url_str_no_scheme = url_str_no_scheme.rstrip(u'/')

			# Emplace the url string in the visited dictionary
			self.visited[url_str_no_scheme] = True

	def _strip_scheme(self, url_str_with_scheme):
		result = self._inner_strip_scheme(url_str_with_scheme, u'https://')
		if result is not None:
			return result

		result = self._inner_strip_scheme(url_str_with_scheme, u'http://')
		if result is not None:
			return result

		return url_str_with_scheme

	def _inner_strip_scheme(self, url_str_with_scheme, scheme):
		idx = url_str_with_scheme.find(scheme) 
		if idx == 0:
			return url_str_with_scheme[idx+len(scheme):]
		return None

	def visited_contains(self, url_str_with_scheme):
		url_str_no_scheme = self._strip_scheme(url_str_with_scheme)
		url_str_no_scheme = url_str_no_scheme.rstrip(u'/')
		return url_str_no_scheme in self.visited
