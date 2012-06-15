#! /usr/bin/python
#Python Version 2.1
#
#
#we need the following module

import httplib
import sys
from optparse import OptionParser

seed ='http://www.houseloan.com/htdocs_folder_list.html'

# request the page
# return entire webpage, status code and status reason
def getURL(page):
    #break Apart web address
    ServerAdr, PagePath = addressBreaker(page)
    #build http connection
    conn = httplib.HTTPConnection(ServerAdr)
    #request connection
    conn.request("GET",PagePath)
    #get response
    r1 = conn.getresponse()
    if r1.status !=200:
      return -1, r1.status, r1.reason
    #save all webpage into data var
    data = r1.read()
	#close the connection cleanly
    conn.close()
    return data, str(r1.status), r1.reason 
  
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
      links.append(url)
      page=page[endpos:]
    else:
      break
  return links

    
def union(p, q):
  for e in q:
    if e not in p:
      p.append(e)

#main engine for crawling the sites
def crawl_web(seed):
  tocrawl=[seed]
  crawled=[]
  index=[]
  while tocrawl:
    page = tocrawl.pop()
    if page not in crawled:
      print page
      content, status, reason = getURL(page) #entire webpage, status code, status reason
      #add_page_to_index(index,page,content)
	 if content != -1:
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
 
#Checks if the link is properly formatted   
def checkPage(page):
  if page.find('http:') == -1:
    print 'Page Error:',page,' incorrectly formated.'
    return ""
  if(page[0]!='h'):
      page = page[page.find('http:'):]
  return page

  
  #####BROKEN NEEDS FIXING
def sanatizeURL(page):
  #if page[0]=='.':
   # page = 'http://'+ServerAdr
  #if page[0]=='/':
   # page = 'http://'+ServerAdr
  if ServerAdr[0]=='.': ServerAdr=domain+ServerAdr[1:]
  tld=ServerAdr[ServerAdr.rfind('.'):]
  domain= ServerAdr[ServerAdr.rfind('.',1,ServerAdr.rfind('.')-1)+1:ServerAdr.rfind('.')]
  return tld, domain
  #if page.find(ServerAdr)==-1:
#    return ""
#  if page.find('http:') ==-1 or page.find('https:')==-1:
 #   page = 'http://'+page
  #else: 
   # return ''  
  #return page
  
#Function breaks apart a link found in a given page
#@input page This is the entire webpage to find contained links.
#@output returns the server path and the remaining page yet to be parsed    
def addressBreaker(page):
  page = checkPage(page)
  if page==-1: 
    return -1, -1
  start_server = page.find('http://')+7
  end_server = page.find('/',page.find('http://')+7)
  server = page[start_server:end_server]
  path = page[end_server:]
  return server,path
  

    
########################################################<module>###################################################################
#call functions
ServerAdr, PagePath = addressBreaker(seed)
##Replace original and force the tld and domain to specific value for CMC webcrawling
#tld, domain = sanatizeURL(ServerAdr)
tld = '.com'
domain = 'houseloan'
crawl_web(seed)
quit()


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