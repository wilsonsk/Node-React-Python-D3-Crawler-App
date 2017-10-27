"""
Filename: arguments.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Contains procedural code to process initial crawl arguments.
"""

from lib.constants import (CL_MAX_TREE_DEPTH, CL_MIN_TREE_DEPTH, CL_MAX_PAGE_LIMIT, CL_MIN_PAGE_LIMIT, CL_DEFAULT_PAGE_LIMIT)
import pprint


def args_validate(argv):
	config = {
		'starting_url' : unicode(argv[1]),
		'search_type' : None,
		'tree_height' : None,
		'crawl_limit' : None,
		'keyword' : None
	}

	idx = 2
	
	if len(argv) < 2:
		raise ValueError('Arguments must contain a search option ("-b" or "-d")')

	if argv[idx] == '-d':
		d_option_validate(argv, config, idx)
	elif argv[idx] == '-b':
		b_option_validate(argv, config, idx)
	else:
		raise ValueError('Invalid search option argument')

	if config['crawl_limit'] is None:
		config['crawl_limit'] = CL_DEFAULT_PAGE_LIMIT

	return config


def b_option_validate(argv, config, idx):
	config['search_type'] = u'-b'
	tree_height = int(argv[idx+1])
	config['tree_height'] = max(tree_height, CL_MIN_TREE_DEPTH) if tree_height < int(CL_MAX_TREE_DEPTH) else CL_MAX_TREE_DEPTH

	if idx+2 < len(argv) and argv[idx+2] == '-l':
		l_option_validate(argv, config, idx+2)
	elif idx+2 < len(argv) and argv[idx+2] == '-k':
		k_option_validate(argv, config, idx+2)
	elif idx+2 < len(argv):
		raise ValueError('Invalid search option argument')


def d_option_validate(argv, config, idx):
	config['search_type'] = u'-d'

	if idx+1 < len(argv) and argv[idx+1] == '-l':
		l_option_validate(argv, config, idx+1)
	elif idx+1 < len(argv) and argv[idx+1] == '-k':
		k_option_validate(argv, config, idx+1)
	elif idx+1 < len(argv):
		raise ValueError('Invalid search option argument')


def l_option_validate(argv, config, idx):
	crawl_limit = int(argv[idx+1])
	config['crawl_limit'] = max(crawl_limit, CL_MIN_PAGE_LIMIT) if crawl_limit < int(CL_MAX_PAGE_LIMIT) else CL_MAX_PAGE_LIMIT

	if idx+2 < len(argv) and argv[idx+2] == '-k':
		k_option_validate(argv, config, idx+2)
	elif idx+2 < len(argv):
		raise ValueError('Invalid keyword option argument')


def k_option_validate(argv, config, idx):
	config['keyword'] = unicode(argv[idx+1])

	if idx+2 < len(argv):
		raise ValueError('Too many command line arguments')