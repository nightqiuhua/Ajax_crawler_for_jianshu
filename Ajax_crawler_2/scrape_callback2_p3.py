import lxml.html 
from pymongo import MongoClient
from datetime import datetime,timedelta
import pymongo
import requests#遇到抓取script变量时，使用requests抓取网页源码
import re

class ScrapeCallback:
	def __init__(self,client=None,expires=timedelta(days=30)):
		self.db = pymongo.MongoClient("localhost",27017).cache
		self.db.user_info.create_index('timestamp',expireAfterSeconds=expires.total_seconds())

	def __call__(self,urls,Downloader):
		for url in urls:
			try:
				html = Downloader(url)
			except Exception as e:
				raise e
			else:
				items={}
				tree = lxml.html.fromstring(html)
				items['title'] = tree.xpath('//div[@class="article"]/h1/text()')[0]
				items['author'] = tree.xpath('//div[@class="info"]/span/a/text()')[0]
				items['author_id'] = re.findall('"id":(.*?),',html,re.S)[0]
				items['date_time'] = tree.xpath('//div[@class="meta"]/span[@class="publish-time"]/text()')[0]
				items['wordage'] = re.findall('"public_wordage":(.*?),',html,re.S)[0]
				items['views_count'] = re.findall('"views_count":(.*?),',html,re.S)[0]
				items['comments_count'] = re.findall('"comments_count":(.*?),',html,re.S)[0]
				items['rewards_count'] = re.findall('"total_rewards_count":(.*?),',html,re.S)[0]
				tpc_seed_url = 'https://www.jianshu.com/notes/{}/included_collections?page=1'.format(items['author_id'])
				to_pages = Downloader(tpc_seed_url)
				total_pages = int(re.findall('"total_pages":(.*?)}',to_pages,re.S)[0])
				items['topic'] = set()
				for tpc_page in range(1,total_pages+1):
					tpc_url ='https://www.jianshu.com/notes/{}/included_collections?page={}'.format(items['author_id'],tpc_page)
					tpc_re = Downloader(tpc_url)
					items['topic'] = items['topic'] | set(re.findall('"title":"(.*?)",',tpc_re,re.S))
				items['topic'] = list(items['topic'])
				print(items)
				self.db.user_info.insert(items)



		
		

