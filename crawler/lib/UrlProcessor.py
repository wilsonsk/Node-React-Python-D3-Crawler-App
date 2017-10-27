"""
Filename: UrlProcessor.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Class for validating URIs, reconstructing relative URIs,
             and performing other URI modifications.
"""

# PYTHON BUILTINS
from urlparse import (urlsplit, urlunsplit)
import re

from utils.utils import errprint

class UrlProcessor:

	def __init__(self, candidate_url=None):
		if candidate_url is None:
			raise TypeError('candidate_url must not be NoneType')
		if not isinstance(candidate_url, unicode):
			raise TypeError('candidate_url must be a Unicode string')
		self.url = candidate_url
		self.parsed_url_tuple = None
	
	def parse_url(self):
		if self.parsed_url_tuple is None:
			try:
				if self.url[:4] != 'http' and self.url[:2] != '//':
					self.url = '//' + self.url
				self.parsed_url_tuple = urlsplit(self.url)
			except (TypeError, AttributeError) as e:
				errprint(e)
				return None
		return True

	def reconstruct(self, hostname=u'', scheme=u'http'):		
		if self.parse_url():
			# Check for scheme existence. If no scheme, add the param scheme.
			if self.parsed_url_tuple[0] == '':
				self.parsed_url_tuple = (scheme,) + self.parsed_url_tuple[1:]  
			# Check for hostname existence. If no hostname, add the param hostname.
			if self.parsed_url_tuple[1] == '' and hostname != u'':
				self.parsed_url_tuple = self.parsed_url_tuple[:1] + (hostname,) + self.parsed_url_tuple[2:]
			elif hostname == u'':
				raise TypeError("Cannot reconstruct without specified hostname")
			# Reassemble the URL into an absolute URL.
			self.url = urlunsplit(self.parsed_url_tuple)

	def extract_robots_url(self):
		if self.parse_url():
			parsed_copy = list(self.parsed_url_tuple)
			parsed_copy[3] = parsed_copy[4] = ''
			parsed_copy[2] = 'robots.txt'
			if self.parsed_url_tuple[0] != '' and self.parsed_url_tuple[1] != '':
				#errprint(urlunsplit(tuple(parsed_copy)))
				return urlunsplit(tuple(parsed_copy))
			else:
				raise ValueError("Cannot extract robots.txt URL from URL without scheme or hostname")

	def validate(self):
		valid_schemes = [u'http', u'https']

		if self.parse_url():
			# Validate number of attributes. We don't want to crawl URLs with user or password information in them.
			if len(self.parsed_url_tuple) != 5:
				return False
			# Validate scheme
			if self.parsed_url_tuple[0] not in valid_schemes:
				return False
			# Validate hostname
			if self.parsed_url_tuple[1] == '' or re.search(r'[:/\?\#\[\]@]', self.parsed_url_tuple[1]):
				return False
			# Validate path
			if self.parsed_url_tuple[2] != '' and re.search(r'[\?\#\[\]]', self.parsed_url_tuple[2]):
				return False
			# Validate query
			if self.parsed_url_tuple[3] != '' and re.search(r'[\?\#\[\]]', self.parsed_url_tuple[3]):
				return False
			# Validate fragment
			if self.parsed_url_tuple[4] != '' and re.search(r'[\?\#\[\]]', self.parsed_url_tuple[4]):
				return False
			return True

	def process(self, absoluteUriArchetype):
		baseUriArchetype = getBaseUri(absoluteUriArchetype)

		if self.url.find(u'http') == 0:
			# Don't do anything. We already have an absolute URI.
			pass

		elif self.url.find(u'//') == 0:
			# Replace archetype from hostname onward
			self.url = doubleSlashCase(baseUriArchetype, self.url)

		elif self.url.find(u'/') == 0:
			# Replace archetype from path onward
			self.url = singleSlashCase(baseUriArchetype, self.url)

		elif self.url.find(u'..') == 0:
			# Recursively strip off everything up to previous slash in Base URI
			self.url = doubleDotCase(baseUriArchetype, self.url)

		elif self.url.find(u'.') == 0:
			# Replace archetype from base path onward
			self.url = singleDotCase(baseUriArchetype, self.url)

		else:
			# Attempt concatenation of relative with base path
			self.url = elseCase(baseUriArchetype, self.url)


def getBaseUri(absoluteUri):
	abs_uri_tuple = urlsplit(absoluteUri)

	path = abs_uri_tuple.path

	lastSlashIdx = path.rfind(u'/')
	path = path[:lastSlashIdx+1]
	if path == u'':
		path = u'/'

	abs_uri_tuple = abs_uri_tuple[:2] + (path,) + abs_uri_tuple[3:]
	return urlunsplit(abs_uri_tuple)

def doubleSlashCase(baseUriArchetype, relativeUri):
	base_uri_tuple = urlsplit(baseUriArchetype)
	base_scheme = base_uri_tuple[0]
	return base_scheme + u':' + relativeUri

def singleSlashCase(baseUriArchetype, relativeUri):
	base_uri_tuple = urlsplit(baseUriArchetype)

	new_uri_tuple = base_uri_tuple[:2] + (relativeUri,) + base_uri_tuple[3:]
	return urlunsplit(new_uri_tuple)

def doubleDotCase(baseUriArchetype, relativeUri):
	base_uri_tuple = urlsplit(baseUriArchetype)
	base_path = base_uri_tuple[2]
	#if base_path[-1] == u'/':
	#	base_path = base_path[:-1]

	base_path, relativeUri = recursiveProcessDoubleDot(base_path, relativeUri)

	# Eat remaining dot-dot operators in the relative URI
	while relativeUri.find(u'../') == 0:
		relativeUri = relativeUri[3:]

	new_path = base_path + relativeUri

	new_uri_tuple = base_uri_tuple[:2] + (new_path,) + base_uri_tuple[3:]
	return urlunsplit(new_uri_tuple)

def recursiveProcessDoubleDot(base_path, relativeUri):
	# Base case: No leading '..'
	if base_path == u'':
		return u'/', relativeUri
	if relativeUri.find('..') != 0 or len(base_path) <= 0:
		return base_path, relativeUri

	# Recursive case: Leading '..'
	relativeUri = relativeUri[2:].lstrip(u'/')
	base_path = base_path[:(base_path.rfind(u'/', 0, (len(base_path)-1))+1)]
	return recursiveProcessDoubleDot(base_path, relativeUri)

def singleDotCase(baseUriArchetype, relativeUri):
	base_uri_tuple = urlsplit(baseUriArchetype)
	base_path = base_uri_tuple[2]
	
	if relativeUri == u".":
		return baseUriArchetype

	new_path = base_path
	if new_path[-1] != u'/':
		new_path = new_path + u'/'

	relativeUri.lstrip(u'.')
	idx = relativeUri.find(u'/')
	if idx != -1:
		new_path = base_path + relativeUri[idx+1:]
		new_uri_tuple = base_uri_tuple[:2] + (new_path,) + base_uri_tuple[3:]
		return urlunsplit(new_uri_tuple)
	else:
		raise ValueError("Invalid current directory relative URI specification. Cannot parse URI.")

def elseCase(baseUriArchetype, relativeUri):
	base_uri_tuple = urlsplit(baseUriArchetype)
	base_path = base_uri_tuple[2]

	new_path = base_path + relativeUri
	new_uri_tuple = base_uri_tuple[:2] + (new_path,) + base_uri_tuple[3:]
	return urlunsplit(new_uri_tuple)


def main():
	uv = UrlProcessor(u'http://www.google.com/##')
	print uv.validate()
	
	uv = UrlProcessor(u'https://moz.com/top500')
	print uv.validate()
	print '-'*10
	uv = UrlProcessor(u'//www.google.com')
	uv.reconstruct('www.google.com')
	print uv.url
	print uv.extract_robots_url()
	print '-'*10
	uv = UrlProcessor(u"/wiki/File:Brandenburg_Brassey%27s.png")
	uv.reconstruct('en.wikipedia.org')
	print uv.url
	print uv.extract_robots_url()
	print '-'*10
	uv = UrlProcessor(u"//upload.wikimedia.org/wikipedia/commons/thumb/4/41/SMS_Kurf%C3%BCrst_Friedrich_Wilhelm_1903.jpg/220px-SMS_Kurf%C3%BCrst_Friedrich_Wilhelm_1903.jpg")
	uv.reconstruct('en.wikipedia.org')
	print uv.url
	print uv.extract_robots_url()

if __name__ == '__main__':
	main()
