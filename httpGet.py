#! /usr/bin/python
#Python Version 2.1
#
#
#we need the following module

import httplib
import sys
from optparse import OptionParser

#seed ='http://www.houseloan.com/htdocs_folder_list.html'
seed = 'http://www.redkeep.com/about.php'
masterTLD = ['.com','.edu','.org']

# request the page
#@input page link to a single webpage
#@output data entire webpage code
#@output status code 
#@output status reason
def getURL(page):
    #break Apart web address
    ServerAdr, PagePath = addressBreaker(page)
    #build http connection
    conn = httplib.HTTPConnection(ServerAdr)
    print ServerAdr," ",conn
    #request connection
    conn.request("GET",PagePath)
    #get response
    r1 = conn.getresponse()
    if r1.status !=200: return -1, r1.status, r1.reason
    #save all webpage into data var
    data = r1.read()
	#close the connection cleanly
    conn.close()
    return data, str(r1.status), r1.reason 
  
#parse the page and return the part within a HREF tag
#@input page a single web page to parse through
#@output url a given url
#@output end_quote the position of the final quote
def get_next_target(page): 
    start_link=page.find('href=')
    if start_link ==-1:
      return None,0
    start_quote=start_link+5
    temp_Quote=page[start_quote] #grabs the type of quote " or '
    end_quote=page.find(temp_Quote,start_quote+1) #looks for the other end of the given quote above
    url=page[start_quote+1:end_quote]
    return url,end_quote

#Calls the get_next_target method to retrieve web links one link at a time, and saves 
#to an array named links.
#@input page
#@links array of links contained within a given page
def get_all_links(page):
  links=[]
  while True:
    url, endpos = get_next_target(page) #ensure page is not error
    #######CHECK if URL is within parent domain#########
    url = sanatizeURL(url, domain)
    if url:
      url = checkDomain(url,domain)
      links.append(url)
      page=page[endpos:]
    else:
      break
  return links

    
#Union function takes array q and adds contents into array p
#@input p final array to work with later
#@input q array that contains items to added into array p
def union(p, q):
  for e in q:
    if e not in p:
      p.append(e)

#main engine for crawling the sites
#@input seed URL link of page to start crawling
#@output crawled array of links crawled
def crawl_web(seed):
  tocrawl=[seed] #array of links to crawl
  crawled=[] #array of links crawled
  index=[] #array of keywords for search engine
  while tocrawl:
    page = tocrawl.pop() #a single link to crawl
    if page not in crawled:
      print page
      content, status, reason = getURL(page) #entire webpage, status code, status reason 
      #add_page_to_index(index,page,content)
      union(tocrawl, get_all_links(content)) #add get_all_links into array tocrawl
      crawled.append(page)  
  return crawled 
  #return index   
    
#Add keyword and url to index array 
def add_to_index(index,keyword,url):
  for entry in index:
    if entry[0] == keyword:
      entry[1].append(url)
      return
  index.append([keyword,[url]])
  
## Function used when working as a search engine crawler
def add_page_to_index(index, url, content):
  words = content.split()
  for word in words:
    add_to_index(index, word, url)
 
#Checks if the link is properly formatted
#@input page
#@output page
#@error return blank to page.
def checkPage(page):
  if page.find('http:') == -1:
    print 'Page Error:',page,' incorrectly formated.'
    return ""
  if(page[0]!='h'):
      page = page[page.find('http:'):]
  return page

  
#checks for url that contains ./ or / or is not a url
#@input page url of page to crawl
#@output page sanitized page or url
def sanatizeURL(page, serverAdr):
  if page == None or len(page)==0:return None
  page = page.strip()
  if page.find('../') != -1:
    if page.find('../') != 0:
      print 'Error: improper format - ',page 
      return None
    page = 'http://'+serverAdr+page[2:]
  if page.find('./') != -1:
    if page.find('./') != 0:
      print 'Error: improper format - ',page 
      return None
  if page[0]=='.': page = 'http://'+serverAdr+page[1:]
  if page[0]=='/': page = 'http://'+serverAdr+page
  if page[-1]=='/': page = page[0:-1]
  if page[0]=='#':return None
  return page
    
#Searches through the hard coded masterTLD array for documented tlds.
#@input serverAdr basic server address
#@output -1 for error will strip out any given subdomains and return root domain
def findDomain(serverAdr):
  for e in masterTLD:
    if ServerAdr.find(e)!=-1:
      tld=ServerAdr[ServerAdr.rfind('.'):]
      domain= ServerAdr[ServerAdr.rfind('.',1,ServerAdr.rfind('.')-1)+1:ServerAdr.rfind('.')]
      return domain+tld
  return -1
  
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

#function checks that the domain is within the target domain
#@input url url link of page
#@input domain server address of the parent domain
def checkDomain(url, domain):
    ServerAdr, PagePath = addressBreaker(url)
    if domain == findDomain(ServerAdr):return url
    else: return None

    
########################################################<module>###################################################################
#call functions
ServerAdr, PagePath = addressBreaker(seed)
domain = findDomain(ServerAdr)
crawl_web(seed)
quit()