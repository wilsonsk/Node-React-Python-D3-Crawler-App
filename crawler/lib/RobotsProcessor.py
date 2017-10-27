"""
Filename: RobotsProcessor.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Class for processing, storing, and retrieving robots.txt files.
"""

# CONSTANTS
from constants import (CRAWLER_MAX_TIMEOUT, CRAWLER_USER_AGENT, RECORD_STALE_SECONDS, RECORD_MAX_BYTES, RECORD_MAX_REDIRECTS)
# LIB
from dbManager import dbManager
from RobotsParser import RobotsParser
# REQUESTS
import requests
# BUILTINS
from datetime import datetime
import re, logging
# UTILS
from utils.request_utils import request_page_crawl
from utils.utils import errprint

class RobotsProcessor(dbManager):
	def __init__(self, url=None):
		if url is None:
			raise TypeError('Parameter url must not be NoneType')
		if not isinstance(url, unicode):
			raise TypeError('Parameter url must be a Unicode string')

		self.url = url
		self.valid_record_count = 0

	
	def acquire_document(self):
		self.conn_wrap(self._acquire_document)

	def _acquire_document(self):
		db = self.client.crawler_db
		robots = db.robots
		
		document = robots.find_one( {'url' : self.url} )

		# Existing document cannot be found
		if document is None:
			# Download the robots txt file and store it in a document.
			errprint(u"Crawler: RobotsProcessor: Acquiring document from scratch")
			self.download_and_store()
		# Document exists, but is in invalid state. This could be due to an SSL security issue with Requests for Ubuntu. In this case, set full allow.
		elif document is not None and 'timestamp' not in document:
			errprint(u"Crawler: RobotsProcessor: Error in acquiring document timestamp. Setting full allow...")
			robots.delete_many( { 'url' : self.url} )
			self._set_full_allow()
		# Document already exists, but more than two weeks have passed since its timestamp.
		elif (datetime.utcnow() - document['timestamp']).total_seconds() > RECORD_STALE_SECONDS:
			# Download the robots txt file and replace the document.
			errprint(u"Crawler: RobotsProcessor: Timestamp is stale. Redownloading document")
			robots.delete_many( { 'url' : self.url} )
			self.download_and_store()
		# Document is good to go. We have a recently updated version of the robots txt file.
		else:
			errprint(u"Crawler: RobotsProcessor: Robots document already exists, so acquisition is unnecessary")


	def download_and_store(self):
		db = self.client.crawler_db
		
		#try:
		#	headers = get_request_headers()
		#	res = requests.get(self.url, stream=True, allow_redirects=False, headers=headers, timeout=CRAWLER_MAX_TIMEOUT)
		#except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.TooManyRedirects) as e:
		#	raise requests.exceptions.HTTPError('Robots request failed. Moving to next queue item.')

		# Attempt to acquire a response object. Throws CrawlerRequestException on failure.
		res = request_page_crawl(self.url, True)
	
		# Process status code.
		status_digit = int(res.status_code) // 100

		# Follow up to 5 redirects, otherwise treat as 4xx.
		if len(res.history) > RECORD_MAX_REDIRECTS:
			errprint(u"Crawler: RobotsProcessor: Max redirects exceeded. Setting full crawl allow.")
			self._set_full_allow()
		# 4xx means "full allow" for crawling.
		elif status_digit == 4:
			errprint(u"Crawler: RobotsProcessor: 4xx status. Setting full crawl allow.")
			self._set_full_allow()	
		# 5xx means "full disallow".
		elif status_digit == 5:
			errprint(u"Crawler: RobotsProcessor: 5xx status. Setting full crawl disallow.")
			self._set_full_disallow()	
		# 2xx means we need to process the file.
		else:
			errprint(u"Crawler: RobotsProcessor: 2xx status. Processing robots.txt file.")
			try:
				self._process_file(res)
			except (ValueError, TypeError) as e:
				#errprint(e)
				self._set_full_allow()

		# Set the timestamp in all cases.
		db.robots.find_one_and_update(
			{ 'url' : self.url },
			{ '$set' : { 'timestamp' : datetime.utcnow() } } )
				

	def _process_file(self, res):
		in_group = False
		curr_bytes = 0
		max_len = 0
		for record in res.iter_lines(decode_unicode=True):
			if record:
				curr_bytes = curr_bytes + len(record.encode('utf-8'))
				if curr_bytes > RECORD_MAX_BYTES:
					break

				parsed_record = RobotsParser(record)
				# Attempt to parse the record. If parsing fails, move on to the next record.
				try:
					parsed_record.parse()
				except ValueError as e:
					#errprint(e)
					continue

				in_group, max_len = self._process_record(parsed_record, in_group, max_len)

		if self.valid_record_count <= 0:
			errprint(u"Crawler: RobotsProcessor: Unable to attain non-user-agent records. Setting full crawl allow.")
			self._set_full_allow()

	def _process_record(self, parsed_record, in_group, max_len):

		db = self.client.crawler_db

		path_pattern = re.compile(parsed_record.path)

		# If we aren't in group and encounter a valid user-agent path, set the state to be in group.
		if not in_group and parsed_record.field == 'user-agent' and re.match(path_pattern, CRAWLER_USER_AGENT):
			#errprint(u"valid initial user-agent sets group to True")
			return True, max_len

		# If we are in group and encounter an invalid user-agent path, take us out of group.
		elif in_group and parsed_record.field == 'user-agent' and not re.match(path_pattern, CRAWLER_USER_AGENT):
			#errprint(u"invalid user-agent takes us out of group")
			return False, max_len

		# If we are in group an encounter a valid user-agent path...
		elif in_group and parsed_record.field == 'user-agent' and re.match(path_pattern, CRAWLER_USER_AGENT):
			#errprint(u"valid user-agent competes with prev user-agent")
			# If the length of the field pattern is longer than the current maximum delete the current set of records.
			if parsed_record.init_path_len > max_len:
				db.robots.delete_many( { 'url' : self.url} )
				return True, parsed_record.init_path_len
			else:
				return False, max_len

		# If we are in group and reach a valid record, then append the record to its robots records list.
		elif in_group and parsed_record.field != 'user-agent':
			#errprint(u"recording valid record")
			self.valid_record_count = self.valid_record_count + 1
			db.robots.find_one_and_update(
				{ 'url' : self.url },
				{ '$push' : { 'entries' : {'field' : parsed_record.field, 'path' : parsed_record.path, 'path_len' : parsed_record.init_path_len} } },
				upsert=True)
			return True, max_len

		# Otherwise, we aren't in group.
		else:
			#errprint(in_group, max_len, parsed_record.field, "nothing happens")
			return False, max_len


	def _set_full_allow(self):
		db = self.client.crawler_db
		db.robots.find_one_and_update(
				{ 'url' : self.url },
				{ '$set' : { 'entries' : [ { 'field' : 'allow', 'path' : '.*', 'path_len' : 1 } ] } },
				upsert=True)

	def _set_full_disallow(self):
		db = self.client.crawler_db
		db.robots.find_one_and_update(
				{ 'url' : self.url },
				{ '$set' : { 'entries' : [ { 'field' : 'disallow', 'path' : '.*', 'path_len' : 1 } ] } },
				upsert=True)

	def permits(self, candidate_url_path):
		return self.conn_wrap(self._permits, candidate_url_path)

	def _permits(self, candidate_url_path):
		candidate_url_path = candidate_url_path[0]
		db = self.client.crawler_db
		document = db.robots.find_one( { 'url' : self.url } )
		
		# If the document can't be retrieved, note that we don't have it and treat it as a full allow.
		if document is None or 'entries' not in document:
			errprint(u"Crawler: RobotsProcessor: No robots document found in datastore for permissions check. Treating as full allow...")
			return True

		entries = document['entries']

		max_len = 0
		state = 'allow'
		for entry in entries:
			if re.match(entry['path'], candidate_url_path) and entry['path_len'] > max_len:
				state = entry['field']
				max_len = entry['path_len']

		return state == 'allow'

if __name__ == '__main__':
	rp = RobotsProcessor('http://support.apple.com/robots.txt')
	rp.acquire_document()