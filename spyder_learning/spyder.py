# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 19:41:20 2016

@author: zhuyongchun
"""

import re
import urllib
import socket
import gzip
import time
import datetime
class Throttle:

	def __init__(self,delay):
		self.delay = delay
		self.domains = {}

	def wait(self,url):
		domain = urllib.parse.urlparse(url).netloc#改为域名
		last_accessed = self.domains.get(domain)
		if self.delay > 0 and last_accessed is not None:
			sleep_secs =self.delay - (datetime.datetime.now() - last_accessed).seconds
			if sleep_secs > 0:
				time.sleep(sleep_secs)
		self.domains[domain] = datetime.datetime.now()

def download(url , user_agent='Mozilla/5.0' , proxy = None , num_retries=2):
	print ('Downloading:',url)
	headers = {'User-agent': user_agent}
	url = url.encode('utf-8')
	url = urllib.parse.quote(url,"://?=&")
	#print(url)
	request = urllib.request.Request(url , headers = headers)
	opener = urllib.request.build_opener()
	if proxy:
		proxy_params = {urllib.parse.urlparse(url).scheme: proxy}
		opener.add_handler(urllib.ProxyHandler(proxy_params))
	try:
		data = opener.open(request,timeout=5).read()
		try:
			decompressed_data = gzip.decompress(data)  #zlib.decompress(data ,16+zlib.MAX_WBITS)
			html = decompressed_data.decode('utf8')
		except:
			html = data.decode('utf8')
			#print(html)
	except urllib.request.URLError as e:
		print ('Download error:', e.reason)
		html=""
		if num_retries>0:
			if hasattr(e,'code') and 500 <= e.code < 600:
				#recursively retry 5xx HTTP errors
				return download(url, num_retries = num_retries-1)
	except socket.timeout as e:
		html=""
		print ("Download error:",e)
	except UnicodeDecodeError as e:
		print ('Download error:',e)
		html=""
	return html

def crawl_sitemap(url): # download the sitemap file
	sitemap = download(url)
	# extract the sitemap links
	links = re.findall('<loc>(.*?)</loc>',sitemap)
	#download each link
	for link in links:
		html = download(link)

def link_crawler(seed_url , user_agent = 'Mozilla/5.0' ,link_regex = '' , max_depth = 5 ,checkmark = '' , delay = 1):
	crawl_queue=[seed_url]
	#keep trace which URL's have seen before
	seen = {}
	seen[seed_url] = 1
	throttle = Throttle(delay)
	while crawl_queue:
		url = crawl_queue.pop()
		depth = seen[url]
		#check url passes robots.txt restrictions
		if depth <= max_depth:
			print (len(crawl_queue))
			#throttle.wait(url)
			html = download(url,user_agent)
			for link in get_links(html):
				#check if link match expected regex
				if re.match(link_regex , link):
					#form absolute link
					link = urllib.parse.urljoin(seed_url, link)
					#check if have already seen this link
					if link not in seen and checkmark in link:
						seen[link]=depth+1
						crawl_queue.append(link)

def get_links(html):
    #a regular expression to extract all links from the webpage
    webpage_regex=re.compile('<a[^>]+href=["\'](.*?)["\']',re.IGNORECASE)
    #list of all links from the webpage
    return webpage_regex.findall(html)

link_crawler('http://www.bnu.edu.cn/')#,checkmark='bnu')