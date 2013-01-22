#! /usr/bin/python
#Python Version 2.1
#
#This script will crawl a web pages links (specified by the seed global variable) and build a tree list 
#and then proceed to crawl those links within the scope of being on the accepted servers list.
#
from bs4 import BeautifulSoup
import urllib2
import re
import time
from urlparse import urlparse
from urlparse import urljoin
import sys

masterTLD = ['.com','.edu','.org']
masterFileFormat = ['.html','.htm','.php','.asp','.aspx','.jsp','.css','.cfm','.doc','.pdf']
skipFileFormat = ['.mp3','.pdf']
#define which servers to stay within - script will not crawl any pages outside these domains
#acceptedServers = ['redkeep.com','jasimmonsv.com']
acceptedServers = ['jasimmonsv.com','redkeep.com']
contentKeywords = re.compile("[Ss]ome [Tt]ext")#RegEx pattern for search for
#vars needed for cookie/session authentication
CFID = '77514'
CFTOKEN = '59455161'
#define your seeded webpage here to begin crawling
try:
    seed=sys.argv[1]
except IndexError:
    seed = 'http://jasimmonsv.com/'

##########################################################
###################CLASSES################################
##########################################################
class WebPage():
    
    #default constructor to build blank WebPage
    def __init__(self, initSeed):
        self.links = []
        self.seed = initSeed
        self.status = str()
        self.reason = str()
        self.server, self.path = addressBreaker(initSeed)
        self.path = str()
        self.brokenImgs = []
        self.contentFlag = False

    #crawl_page function allows the WebPage class to crawl itself using multi-node tree logic
    #@input self self referrer
    #@output none
    def crawl_page(self, parent=None):
        tempArray = []
        if parent != None:
            if parent.seed not in crawled: crawled.append(parent.seed)
            if (parent.seed == self.seed):return
        if (self.seed in crawled): #skips pulling url if already called... need to add another round to data to populate missed data.
            self.status = 100
            self.reason='Already Crawled'
            return
        print str(self.seed)
        if getDomain(self.seed) not in acceptedServers: #check that the page's server is on the acceptedServers list
            content, self.status, self.reason = getURL(self.seed, True) #save status code and status reason
            crawled.append(self.seed) #mark this page as crawled
            return #drop out of this current iteration
        content, self.status, self.reason = getURL(self.seed) #entire webpage, status code, status reason
        crawled.append(self.seed) #add current page to crawled array
        if self.status == '200': #check that page was successfully retrieved.
            union(tempArray, get_all_links(content, self.seed)) #add all links within the page to a temp array
            self.brokenImgs = get_broken_imgs(content, self.seed)
            self.contentFlag = checkContent(str(content))
            for e in tempArray:
                self.links.append(WebPage(e)) #add all links within temp array to self.links array
            for e in range(len(self.links)): #crawl through all the links
                self.links[e].crawl_page(self) #depth-first crawl through self.links array
        else: crawled.append(self.seed)
        return
    #printLinks function prints the links to the screen
    #@input self self referrer
    #@input n level of child node from parent
    def printLinks(self,n):
        print n*'|'+'-'+self.seed
        for e in self.links:
            e.printLinks(n+1)
    
    #savePages function writes the pages to a file pointer f
    #@input self self referrer
    #@input n level of child node from parent
    #@input f file pointer
    #@output none
    def savePages(self, n, f):
        #f.write(n*'|'+'-'+self.seed+':'+str(self.status)+'\n')
        f.write('<Page pageName="'+self.seed+'" status="'+str(self.status)+'">\n')
        for e in self.links:
            e.savePages(n+1, f)
        f.write('</Page>\n')
        
    def troubleReportLinks(self, f):
        for e in self.links:
            if (str(e.status) != '200'): 
                if (str(e.status) != '100'):
                    f.write('"'+str(e.status)+'","'+self.seed+'","'+e.seed+'"\n')
            elif str(e.status) == '200':
                e.troubleReportLinks(f)    

    def troubleReportImgs(self, f):
        for x in self.brokenImgs: 
            f.write('"BrokenImg","'+self.seed+'","'+x+'"\n')
        if self.contentFlag: f.write('"ContentAlert","'+self.seed+'","Keyword Found"\n')
        for e in self.links:
            if str(e.status)=='200':
                e.troubleReportImgs(f)            
##########################################################
#########END CLASSES######################################
##########################################################
    
# request the page
#@input page link to a single webpage
#@output data entire webpage code
#@output status code 
#@output status reason
def getURL(page, passed=False):
    #build http connection
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie','CFID='+CFID+'; CFTOKEN='+CFTOKEN))
    #request connection
    try:
        request = urllib2.Request(page.replace(" ","%20"))
        request.add_header('User-agent','Testing Web Crawling Daemon/2.0')
        r1 = opener.open(request, timeout= 12)
        #get response
        if str(r1.code) != '200': return -1, r1.code, r1.msg
        #close the connection cleanly
        if page[-4:] in skipFileFormat:
            print 'Skipping downloading of '+page[-4:]+' file'
            data = BeautifulSoup()
        elif passed: data=BeautifulSoup()
        else:data = BeautifulSoup(r1.read())
    except Exception as inst:
        print " Error connecting to site: "+str(page)
        if type(inst) == urllib2.HTTPError:
            return -1, inst.code, inst.msg
        else: return -1, 0, inst
    finally:
        opener.close()
    return data, str(r1.code), r1.msg
#Calls the get_next_target method to retrieve web links one link at a time, and saves 
#to an array named links.
#@input page
#@links array of links contained within a given page
def get_all_links(page, ServerAdr):
    links=[]
    if page == -1:return links
    #grab all the image links on the page
    for link in page.find_all('a'):
        passLink = link.get('href')
        if passLink !=None:
            url = sanatizeURL(str(passLink),ServerAdr)
            if url != -1: links.append(url)
    return links

def get_broken_imgs(page, ServerAdr):
    links=[]
    badImages=[]
    if page == -1:return links
    for link in page.find_all('img'):
        passLink = link.get('src')
        if passLink !=None:
            url = sanatizeURL(str(passLink),ServerAdr)
            if url != -1: links.append(url)
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie','CFID='+CFID+'; CFTOKEN='+CFTOKEN))
    for e in links:
        #request connection and check status of images
        try:
            request = urllib2.Request(e.replace(" ","%20"))
            request.add_header('User-agent','Testing Web Crawling Daemon/2.0')
            r1 = opener.open(request, timeout= 12)
            #get response
            if str(r1.code) != '200': badImages.append(e) 
            #close the connection cleanly
        except Exception as inst:
            print " Error connecting to site: "+str(e)
            badImages.append(e)
        finally:
            opener.close()
    return badImages
    return links

def checkContent(page):
    if contentKeywords.search(page):
        return True
    else: return False

#Union function takes array q and adds contents into array p
#@input p final array to work with later
#@input q array that contains items to added into array p
def union(p, q):
    for e in q:
        if e not in p:
            if e not in crawled:
                p.append(e)

 
#Checks page for "http:"
#@input page - a web link to see if the page is a string or unicode, and that it has http: or https in front
#@output page - will return the link that it found to ensure that it works properly.
#@error return -1 if error.
def checkPage(page):
    if page==None: return -1
    page = str(page)
    if not isinstance(page,str):
        if not isinstance(page,unicode):return -1
    if page.find('http:')>=0:
        return page[page.find('http:'):]
    elif page.find('https:')>=0:
        return page[page.find('https:'):]
    #TODO add image checking elif page.find('src='):return page[page.find('src='):]
    else: return -1

  
#takes results of "href=" and transforms into valid link
#@input page url of page to crawl
#@output page sanitized page or url
def sanatizeURL(page, serverAdr):
    assert page != None, "sanatizeURL failed: page type None"
    assert serverAdr != None, "sanatizeURL failed: serverAdr type None"
    assert type(page) == str, str("sanatizeURL failed: page not of type str: {}").format(page) 
    assert type(serverAdr) == str, "sanatizeURL failed"
    assert len(page)>0 or len(serverAdr)>0, "Passed data is missing"
    page = page.strip()
    o = urlparse(page)
    p = urlparse(serverAdr)
    
    if o.scheme == 'mailto':return -1
    if o.path[:2]=='..':return -1
    if  o.netloc == '':
        if o.path == p.netloc+'/':
            o = urlparse('http://'+o.netloc+o.path+o.params+o.query+o.fragment)
        else: o = urlparse(urljoin(serverAdr,o.path))
    if o.path == '':o = urlparse(o.scheme+'://'+o.path+o.netloc+o.path+'/'+o.params+o.query+o.fragment)  
    return o.geturl()
  
  
#Function breaks apart a link found in a given page
#@input page This is a link to find contained links.
#@output returns the server path and the remaining page yet to be parsed    
def addressBreaker(page):
    #page = checkPage(page)
    assert (isinstance(page,str) or isinstance(page,unicode)), str(page)+' is not a str or unicode'
    if not isinstance(page, str):
        if not isinstance(page, unicode):return -1, -1
    if len(page)>0:
        o = urlparse(page)
        return o.netloc ,o.path
    return -1, -1

def getDomain(page):
    server, path = addressBreaker(page)
    if server == -1 or server == None: return -1
    tld = server[server.rfind('.'):]
    server = server[:server.rfind('.')]
    domain = server[server.rfind('.')+1:]
    return domain+tld

def output(rootPage):
    with open('./results.'+str(start)+'.xml','w') as f:
        f.write('<Website>\n')
        rootPage.savePages(0,f)
        f.write('</Website>\n')
    f.closed  
    with open('./openIssues.'+str(start)+'.csv','w') as f:
        f.write('"status","Parent","Link"\n')
        rootPage.troubleReportLinks(f)
        rootPage.troubleReportImgs(f)
    f.closed
########################################################<module>###################################################################

crawled = []
rootPage = WebPage(seed)

if __name__ == "__main__":
    start = time.time()  
    rootPage.crawl_page()
  
    '''output results to files'''
    output(rootPage)
    print 'Time Elapsed: '+str(time.time() - start)
