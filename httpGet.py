#! /usr/bin/python
#Python Version 2.1
#
#
#we need the following module

import httplib
import sys
from optparse import OptionParser

seed ='http://www.redkeep.com/about.php'

# request the page
def getURL(page):
    #break Apart web address
    throwAway, PagePath = addressBreaker(page)
    conn = httplib.HTTPConnection(ServerAdr)
    conn.request("GET",PagePath)
    r1 = conn.getresponse()
    if r1.status !=200:
      return -1, r1.status, r1.reason
    data = r1.read()
    conn.close()
    return data, str(r1.status), r1.reason

def get_page(url):
  try:
    import urllib
    return urllib.urlopen(url).read()
  except:
    return ""
  
#parse the page and return the part within a HREF tag
def get_next_target(page): 
    start_link=page.find('href=')
    if start_link ==-1:
      return None,0
    start_quote=page.find('"',start_link)
    end_quote=page.find('"',start_quote+1)
    url=page[start_quote+1:end_quote]
    return url,end_quote

def get_all_links(page):
  links=[]
  while True:
    url, endpos = get_next_target(page)
    if url:
      url = sanatizeURL(url)
      links.append(url)
      page=page[endpos:]
    else:
      break
  return links

    
def union(p, q):
  for e in q:
    if e not in p:
      p.append(e)

def crawl_web(seed):
  tocrawl=[seed]
  crawled=[]
  index=[]
  while tocrawl:
    page = tocrawl.pop()
    if page not in crawled:
      print page
      content, status, reason = getURL(page)
      #content = get_page(page)
      #add_page_to_index(index,page,content)
      union(tocrawl, get_all_links(content))
      crawled.append(page)  
  return crawled 
  #return index   
    
def add_to_index(index,keyword,url):
  for entry in index:
    if entry[0] == keyword:
      entry[1].append(url)
      return
  index.append([keyword,[url]])
  
def add_page_to_index(index, url, content):
  words = content.split()
  for word in words:
    add_to_index(index, word, url)
 
#Checks if the page is properly formatted   
def checkPage(page):
  if page.find('http:') == -1:
    print 'Page Error:',page,' incorrectly formated.'
    return ""
  if(page[0]!='h'):
      page = page[page.find('http:'):]
  return page

def sanatizeURL(page):
  if page[0]=='.':
    page = 'http://'+ServerAdr+page[1:]
  if page[0]=='/':
    page = 'http://'+ServerAdr+page
  tld=ServerAdr[ServerAdr.rfind('.'):]
  domain=ServerAdr[ServerAdr.rfind(tld):]
  if page.find(ServerAdr)==-1:
    return ""
  if page.find('http:') ==-1 or page.find('https:')==-1:
    page = 'http://'+page
  else: 
    return ''  
  return page
  
    
def addressBreaker(page):
  page = checkPage(page)
  if page==-1: 
    return -1, -1
  start_server = page.find('http://')+7
  end_server = page.find('/',page.find('http://')+7)
  server = page[start_server:end_server]
  path = page[end_server:]
  return server,path
  
#handle the returned stuff and generate a new page
def main():
    # parameter and constants
    
    #checkPage(seed)
    #crawl_web(seed)
    #***********UNIT TESTING*****************
    tld = ServerAdr[ServerAdr.rfind('.'):]
    domain = ServerAdr[ServerAdr.rfind('.',ServerAdr.rfind('.')+1):]
    print tld
    print domain
    print sanatizeURL('redkeep.com')
    # call functions
    quit()
    #

#call main function

ServerAdr, PagePath = addressBreaker(seed)
main() 


#*************************************HOLD SECTION******************************************
#parse the page and return the part within a SRC tag    
def extractSRC(raw, links): 
    position =0
    endIndex = raw.rfind('src=')
    while (position < endIndex):
      links.append(raw[raw.find('src=',position)+5:raw.find('"',raw.find('src=',position)+5)])
      position = raw.find('src=',position)+1
    return
    
#parse through the link array
def extractLinks(links,srvAddy):
  webPath = None
  #print links, srvAddy
  if links.find('http://')!=-1:
    print "found http://"
    srvAddy=links[links.find('http://')+8:links.find('/',links.find('http://')+8)]
    webPath=links[links.find('/',links.find('http://')+8):]
    print srvAddy, webPath
  if links.find('/')==-1:
    webPath = links
  return srvAddy, webPath