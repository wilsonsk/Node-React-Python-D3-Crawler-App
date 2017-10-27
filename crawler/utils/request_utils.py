"""
Filename: request_utils.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Standardized functions for making HTTP requests.
"""
# Requests
import requests
# Exceptions
from exceptions import CrawlerRequestException
# Utils
from utils import errprint
# Constants
from lib.constants import (CRAWLER_USER_AGENT, CRAWLER_MAX_TIMEOUT, RECORD_MAX_REDIRECTS)

def get_request_headers():
	headers = requests.utils.default_headers()
	headers.update(
		{
			'User-Agent' : CRAWLER_USER_AGENT,
		})

	return headers

def get_request_config(robots_request):
	config = {
		"headers" : get_request_headers(),
		"max_redirects" : RECORD_MAX_REDIRECTS,
		"stream" : False,
		"timeout" : CRAWLER_MAX_TIMEOUT,
	}

	if robots_request:
		#config['stream'] = True
		pass

	return config
	
def request_page_crawl(url, robots_request=False):
	config = get_request_config(robots_request)

	try:
		with requests.Session() as s:
			s.max_redirects = config['max_redirects']
			s.stream = config['stream']
			r = s.get(url, headers=config['headers'], timeout=config['timeout'])
		return r
	except requests.exceptions.HTTPError as e:
		errprint(e)
		raise CrawlerRequestException
	except requests.exceptions.ConnectionError as e:
		errprint(e)
		raise CrawlerRequestException
	except requests.exceptions.TooManyRedirects as e:
		errprint(e)
		raise CrawlerRequestException
	except Exception as e:
		errprint(e)
		raise CrawlerRequestException

def handleRobotsResponse(res):
	if testRobotsResponse(res):
		errprint(r.url)
		errprint(r.headers)

		for line in r.iter_lines():
			if line:
				print line

def testRobotsResponse(res):
	if res is None:
		return False

	if res.headers is None or res.headers['Content-Type'] is  None:
		return False
	
	return True