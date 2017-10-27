# -*- coding: utf-8 -*-

"""
Filename: crawler.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Contains the main crawler loop as well as main function utilities.
"""

# BUILTINS
import codecs, json, os, random, sys, time, pprint
from datetime            import datetime
# CONSTANTS
from lib.constants 		 import (CL_MAX_TREE_DEPTH, SYS_STDOUT_ENCODING)
from lib.constants 		 import (EXIT_STATUS_OK, 
	EXIT_STATUS_INVALID_ARGS, EXIT_STATUS_INVALID_STARTING_URL, EXIT_STATUS_INVALID_READ)
# LIB
from lib.CrawlManager    import CrawlManager
from lib.UrlProcessor    import UrlProcessor
from lib.UrlQueue        import UrlQueue
from lib.RobotsProcessor import RobotsProcessor
from lib.Scraper         import Scraper
# UTILS
from utils.arguments     import args_validate
from utils.exceptions    import CrawlerRequestException
from utils.request_utils import request_page_crawl
from utils.utils         import (errprint, erroutput)
# REQUESTS
import requests


def main():
	try:
		config = args_validate(sys.argv)
	except Exception as e:
		errprint(e)
		errprint(u'Crawler: Invalid syntax to begin crawl. Usage: crawler.py starting_url -d | <-b tree_height> [-l crawl_limit] [-k keyword]')
		erroutput(EXIT_STATUS_INVALID_ARGS)
		sys.exit(EXIT_STATUS_INVALID_ARGS)	
	_main(config)


def _main(config):

	crawl_mgr = CrawlManager(config)
	outfile = 'CRAWLER_OUTPUT-{0}-{1}'.format( datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f"), os.getpid() )

	# Initialize the URL Queue, including validating the starting URL.
	try:
		crawl_mgr.queue.initialize(config['starting_url'])
	except ValueError as e:
		errprint("Crawler: Invalid starting URL.")
		erroutput(EXIT_STATUS_INVALID_STARTING_URL)
		sys.exit(EXIT_STATUS_INVALID_STARTING_URL)

	# MAIN LOOP BEGINS - Continue until URL Queue is empty - May want to bail out under other circumstances as well (e.g. timeout, certain number of URLs processed).
	while len(crawl_mgr.queue) > 0 and crawl_mgr.count <= config['crawl_limit']:	
		
		errprint(u"-"*20)

		# Dequeue a URL - URLs are validated prior to enqueuing.
		current_obj = crawl_mgr.queue.pop()
		current_url, parent_url, depth, url_title = crawl_mgr.queue.split_node(current_obj)

		# Check depth in BFS. If max depth or config depth exceeded, exit the loop
		if config['search_type'] == '-b' and (depth > CL_MAX_TREE_DEPTH or depth > config['tree_height']):
			errprint('Crawler: Main: Max depth exceeded. Ending crawl...')
			break

		errprint( "Crawler: Main: Currently visiting: {0}".format(current_url.url.encode('utf-8')) )

		if crawl_mgr.visited_contains(current_url.url):
			errprint(u"Crawler: Main: Already crawled item. Continuing to next item...")
			continue

		# Add current URL to the visited dictionary without a scheme (to avoid HTTP/HTTPS circles)
		crawl_mgr.emplace_visited(current_url.url)

		# Check database for up-to-date information on a given URL. If it exists, skip the request step and move directly to selection and enqueueing.
		child_possibilities, url_title = crawl_mgr.get_links(current_url.url)

		if config['keyword'] is not None or child_possibilities is None:
			
			errprint(u'Crawler: Main: No database info available for current URL.')

			# Acquire and process robots.txt belonging to the current URL. Ship relevant robots.txt data to the database if it isn't already present.
			rp = RobotsProcessor(current_url.extract_robots_url())
			try:
				rp.acquire_document()
			except CrawlerRequestException:
				if crawl_mgr.count == 0:
					errprint(u'Crawler: Unable to obtain robots.txt file for starting URL.')
					erroutput(EXIT_STATUS_INVALID_STARTING_URL)
					sys.exit(EXIT_STATUS_INVALID_STARTING_URL)
				errprint("Crawler: Main: Robots request failed. Moving to next queue item.")
				continue 

			# Validate the current URL against the robots.txt policies - Discard current URL if crawling is disallowed.
			candidate_path =  current_url.parsed_url_tuple[2]
			if not rp.permits(candidate_path if candidate_path != '' else u'/'):
				errprint( u'Crawler: Main: Robots.txt disallows crawling for {0}.'.format(current_url.url.encode('utf-8')) )
				continue

			# Crawl the page. If we find a possible hit, validate its syntax and add it to queue possibilities. Continue until we hit maximum possibilities for queue.
			s = Scraper(current_url.url)
			
			try:
				scraped_urls, url_title, keyword_found, canonical_url = s.scrape_url(config['keyword'])
			except CrawlerRequestException:
				if crawl_mgr.count == 0:
					errprint(u'Crawler: Request to obtain starting URL failed.')
					erroutput(EXIT_STATUS_INVALID_STARTING_URL)
					sys.exit(EXIT_STATUS_INVALID_STARTING_URL)
				errprint(u'Crawler: Main: Failed to scrape URL. Moving to next queue item...')
				continue
			
			# Avoid cycles with in visiting the canonical_url
			crawl_mgr.emplace_visited(canonical_url)

			# Attempt to validate/reconstruct partial URLs
			reconstructed_possibilities = validate_and_reconstruct(current_url, scraped_urls, crawl_mgr)

		else:
			errprint( u'Crawler: Main: Database info available for current URL.')
			reconstructed_possibilities = []
			keyword_found = False
			for url in child_possibilities:
				#if url not in crawl_mgr.visited:
				if not crawl_mgr.visited_contains(url):
					reconstructed_possibilities.append(url)

		# If not already in the database, place the next URL(s) and the current URL as parent to the next URLs in the database.
		if child_possibilities is None:
			crawl_mgr.set_links(current_url.url, reconstructed_possibilities, url_title)
		
		# Process possible links. For both BFS and DFS, shuffle the existing links and place them in the list of child nodes to visit.
		children_to_visit = process_possible_links(reconstructed_possibilities, 
			True if config['search_type'] == '-d' else False)
		if len(children_to_visit) <= 0:
			errprint(u"Crawler: Main: No links found at current node.")

		# DFS ONLY - Reset the queue on successful runs prior to enqueuing
		if config['search_type'] == '-d':
			crawl_mgr.queue.queue.clear()
			#crawl_mgr.cooldown[current_url.parsed_url_tuple[1]] = datetime.utcnow()

		# Enqueue links and store for final transmission
		for link in children_to_visit:
			crawl_mgr.queue.push(link, current_url, depth, url_title)

		# Write the intermediate result to file
		parent_url = None if parent_url is None else parent_url.url
		out_obj = generate_link_obj(parent_url, current_url.url, depth, url_title, keyword_found)

		with open(outfile, "a") as f:
			f.write(json.dumps(out_obj, ensure_ascii=False).encode(SYS_STDOUT_ENCODING, errors='replace'))
			f.write(u'\n'.encode(SYS_STDOUT_ENCODING, errors='replace'))
		
		# Increment the number of crawled URLs
		crawl_mgr.count = crawl_mgr.count + 1
		
		# If we've found the keyword, break out.
		if keyword_found:
			break

	# Hold off until the crawl is completed and send all data back at once.
	try:
		with open(outfile, "r") as f:
			sep = u''
			print(u'[')
			for line in f:
				print(sep)
				print(line)
				sep = u','
			print(u']')
	except IOError as e:
		errprint("Crawler: Main: Error reading output file: " + str(e))
		errprint(u'Crawler: Error reading output file for final output')
		erroutput(EXIT_STATUS_INVALID_READ)
		sys.exit(EXIT_STATUS_INVALID_READ)

	if crawl_mgr.count == (config['crawl_limit'] + 1):
		errprint(u"Crawler: Crawl ended successfully and hit the page limit.")
	else:
		errprint(u"Crawler: Crawl ended successfully before hitting the page limit.")
	erroutput(EXIT_STATUS_OK)
	sys.exit(EXIT_STATUS_OK)


def validate_and_reconstruct(current_url, scraped_urls, crawl_mgr):
	# Attempt to validate/reconstruct partial URLs
	reconstructed_possibilities = []
	scheme = current_url.parsed_url_tuple[0]
	hostname = current_url.parsed_url_tuple[1]
	for url in scraped_urls:
		up = UrlProcessor(url)
		up.process(current_url.url)
		if up.validate()and not crawl_mgr.visited_contains(up.url): 
			reconstructed_possibilities.append(up.url)
	return reconstructed_possibilities


def process_possible_links(reconstructed_possibilities, is_dfs):
	children_to_visit = []
	if len(reconstructed_possibilities) > 0:
		children_to_visit = reconstructed_possibilities[:]
		if is_dfs:
			random.shuffle(children_to_visit)
	return children_to_visit


def generate_link_obj(parent, child, height, child_title, keyword_found):
	out_obj = {
		'parent' : parent,
		'child' : child,
		'title': child_title,
		'height' : height,
		'keyword_found' : keyword_found
	}
	return out_obj


if __name__ == '__main__':
	main()