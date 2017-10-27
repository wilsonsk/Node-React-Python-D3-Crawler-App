"""
Filename: UrlQueue.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Helper class for initializing and managing the URL queue
             within the main URL queue loop.
"""

# BUILTINS
from collections import deque
# LIB
from UrlProcessor import UrlProcessor


class UrlQueue:

	def __init__(self):
		self.queue = deque()

	def __len__(self):
		return len(self.queue)

	def initialize(self, init_url):
		url = UrlProcessor(init_url)
		url.parse_url()
		url.reconstruct(url.parsed_url_tuple[1])

		if not url.validate():
			raise ValueError("Starting URL must be a valid absolute URL")
		
		obj = {'child' : url,
				'parent' : None,
				'depth' : 0}

		self.queue.appendleft(obj)

	def push(self, url, parent, prev_depth, title):
		url = UrlProcessor(url)
		if url.validate():

			obj = {'child' : url,
					'parent' : parent,
					'depth' : prev_depth + 1,
					'title' : title}

			self.queue.appendleft(obj)
			
	def pop(self):
		return self.queue.pop()

	def split_node(self, node):
		if 'title' not in node:
			node['title'] = None

		return (node['child'], node['parent'], node['depth'], node['title'])