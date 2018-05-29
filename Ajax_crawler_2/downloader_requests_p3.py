import urllib.parse 
import socket 
from datetime import datetime 
import time 
import random 
import requests
import lxml.html

DEFAULT_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
DEFAULT_DELAY = 2
DEFAULT_TIMEOUT = 60
DEFAULT_RETRIES = 1

class Throttle:
	def __init__(self,delay):
		self.delay = delay
		self.domains = {}

	def wait(self,url):
		domain = urllib.parse.urlparse(url).netloc
		last_accessed = self.domains.get(domain)

		if self.delay > 0 and last_accessed is not None:
			sleep_sec = self.delay-(datetime.now() - last_accessed).seconds
			if sleep_sec>0:
				time.sleep(sleep_sec)
		self.domains[domain] = datetime.now()

class Downloader:
	def __init__(self,delay=DEFAULT_DELAY,user_agent=DEFAULT_AGENT,proxies=None,num_tries=DEFAULT_RETRIES,timeout=DEFAULT_TIMEOUT,opener=None,cache=None):
		socket.setdefaulttimeout(timeout)
		self.throttle = Throttle(delay)
		self.user_agent=user_agent 
		self.proxies = proxies 
		self.num_tries=num_tries
		self.cache = cache
		self.opener = opener

	def __call__(self,url):
		result = None
		if self.cache:
			try:
				result = self.cache[url]
			except KeyError:
				pass
			else:
				if self.num_tries > 0 and 500<=result['code'] <600:
					result = None
		if result is None:
			self.throttle.wait(url)
			proxy = random.choice(self.proxies) if self.proxies else None
			headers = {'Accept':"text/html, application/xhtml+xml, */*",'X-Requested-With': 'XMLHttpRequest','User-Agent':self.user_agent}
			result = self.download(url,headers,proxy=proxy,num_tries=self.num_tries)
			if self.cache:
				self.cache[url] = result
		return result['html']

	def download(self,url,headers=None,proxy=None,num_tries=2,data=None):
		print('Downloading:',url)
		arguments = {}
		if proxy:
			arguments['proxy'] = proxy
		if headers:
			arguments['headers'] = headers
		try:
			response = requests.get(url,headers=arguments['headers'])
			html = response.text
			code = response.status_code
		except Exception as e:
			print('Download error:',e)
			html = ''
			if hasattr(e,'code'):
				code = e.code
				if num_tries >0 and 500<=code<600:
					html = self.download(url,headers,proxy,num_tries-1)
			else:
				code = response.status_code
		return {'html':html,'code':code}
