"""
Filename: dbManager.py
Author: Maxwell Goldberg
Last modified: 06.09.17
Description: Base class for database access.
"""

# DATABASE SUPPORT
from pymongo import MongoClient
import pymongo
# PYTHON BUILTINS
import logging

# Initialize client connection

class dbManager:
	def __init__(self):
		pass

	def connect(self):
		try:
			# Alter this string in order to change the location of the database the crawler connects to.
			self.client = MongoClient('mongodb://localhost:27017/')
		except pymongo.errors.ConnectionFailure as e:
			errprint(e)

	def close(self):
		try:
			self.client.close()
		except AttributeError as e:
			errprint(e)

	def conn_wrap(self, fn, *args):
		self.connect()
		if args:
			ret_val = fn(args)
		else:
			ret_val = fn()
		self.close()
		return ret_val