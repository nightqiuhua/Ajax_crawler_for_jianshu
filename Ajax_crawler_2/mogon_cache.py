try:
	import cPickle as pickle 
except ImportError:
	import pickle
import zlib
from pymongo import MongoClient 
from datetime import datetime,timedelta 
from bson.binary import Binary

class MongoCache:
	def __init__(self,client=None,expires=timedelta(days=30)):
		self.client = MongoClient("localhost",27017) if client is None else client 
		self.db = self.client.cache 
		self.db.webpage.create_index('timestamp',expireAfterSeconds=expires.total_seconds())


	def __contains__(self,url):
		try:
			self[url]
		except KeyError:
			return False
		else:
			return True 

	def __getitem__(self,url):
		if len(url) > 100:#url过长，无法插入mongdb,采取截短后，再插入mongdb
			cache_url = url[len(url)-100:len(url)-1]#以url最后100个字符为特征
		else:
			cache_url = url
		record = self.db.webpage.find_one({'_id':cache_url})
		if record:
			return pickle.loads(zlib.decompress(record['result']))
		else:
			raise KeyError(url + 'does not exist')

	def __setitem__(self,url,result):
		if len(url) > 100:
			cache_url = url[len(url)-100:len(url)-1]
		else:
			cache_url = url
		record = {'result':Binary(zlib.compress(pickle.dumps(result))),'timestamp':datetime.utcnow()}
		self.db.webpage.update({'_id':cache_url},{'$set':record},upsert=True)

	def clear():
		self.db.webpage.drop()