import re 
import datetime 
import time 
from downloader_requests_p3 import Downloader
from mogon_cache import MongoCache
from scrape_callback2_p3 import ScrapeCallback
import lxml.html


def link_crawler(seed_url,page,link_regx=None,delay=5,max_depth=2,max_urls=-1,user_agent=None,proxies=None,num_retries=1,scrape_callback=None,cache=None):
	D = Downloader(delay=delay,user_agent=user_agent,proxies=proxies,num_tries=num_retries,cache=cache)
	main_url = seed_url
	append_ids = ''
	sub_seen = []
	for page in range(0,5):
		url = seed_url + '?page={}'.format(page)+append_ids
		try:
			html = D(url)
		except Exception as e:
			raise e
		else:
			tree = lxml.html.fromstring(html)
			temp_sub_urls= []
			sub_urls=[]
			if scrape_callback:
				temp_sub_urls = tree.xpath('//div[@class="content"]/a/@href')
				for sub_url in temp_sub_urls:
					sub_url = 'https://www.jianshu.com'+sub_url
					if sub_url not in sub_seen:
						sub_urls.append(sub_url)
						sub_seen.append(sub_url)
				scrape_callback.__call__(sub_urls,D)
			id_infos = tree.xpath('//li/@data-note-id')
			for id_info in id_infos:
				append_ids +='&seen_snote_ids%5B%5D={}'.format(id_info)

	

seed_url = 'https://www.jianshu.com/trending/weekly'
page = 1
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
link_crawler(seed_url=seed_url,page = 1,user_agent=user_agent,scrape_callback=ScrapeCallback(),cache = MongoCache())