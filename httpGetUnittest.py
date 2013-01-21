#! /usr/bin/python
#Python Version 2.7

import unittest
import httpGet as hg

class TestCheckPage(unittest.TestCase):
  def setUp(self):
    link=1
	
  def runTest(self):
    pass
	
class TestAddressBreaker(unittest.TestCase):
  def setUp(self):
    self.link = [['http://a1.com','/'],
	             ['https://a2.com','/'],
				 ['ftp://a3.com','/'],
				 ['www.a4.com','/'],
				 ['a5.com','/'],
				 ['www.a6.com/index','a6.com','/index'],
				 ['www.a7.com/index.html','a7.com','/index.html'],
				 ['www.a8.com/index?testing','a8.com','/index'],
				 ['www.a9.com/index?testing=1234','a9.com','/index'],
				 ['www.a10.com/index?testing=134#blah','a10.com','index']
				]
	
  def runTest(self):
    for x in range(len(self.link)):
	  assert hg.addressBreaker(self.link[x][0])==self.link[x][1]
	
class TestGetDomain(unittest.TestCase):
  def setUp(self):
    self.link = [['http://a1.com','a1.com'],
	             ['https://a2.com','a2.com'],
				 ['ftp://a3.com','a3.com'],
				 ['www.a4.com','a4.com'],
				 ['a5.com','a5.com'],
				 ['www.a6.com/index','a6.com'],
				 ['www.a7.com/index.html','a7.com'],
				 ['www.a8.com/index?testing','a8.com'],
				 ['www.a9.com/index?testing=1234','a9.com'],
				 ['www.a10.com/index?testing=134#blah','a10.com']
				]
  
  def runTest(self):
    for x in range(len(self.link)):
	  assert hg.getDomain(self.link[x][0])==self.link[x][1]
  
class TestSanitizeURL(unittest.TestCase):
  def setup(self):
    links={'http://google.com/':1,
	       'www.google.com':1,
		   'google.com':0,
		   'www.google.com?testing=this stuff':1,
		   'google.com/':1,
		   'https://google.com':1,
		   'ftp://google.com':0
		   }
    pass
  
  def properLinks(self):
    #hg.SanitizeURL(links[x])
	pass


if __name__ == '__main__':
  unittest.main()