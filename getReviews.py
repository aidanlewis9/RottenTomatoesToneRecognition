#!/usr/bin/env python2.7

import os
import sys
import commands
import re

def getURLs():
   urls = []
   for year in range(1915, 2017):
      titles = []
      yearURL = "https://en.wikipedia.org/wiki/List_of_American_films_of_" + str(year)
      trash, html = commands.getstatusoutput("curl {}".format(yearURL))
      titles += re.findall(r"<td><i><a href=\"/wiki/([^\"]*)\" title=", html)
      for t in titles:
         title = t.lower().strip().replace("%27", "").replace("%26", "and").replace(":", "").replace("!", "").replace("%3f", "")
         if title.find(str(year)) != -1:
            regex1 = "_(" + str(year) + "_film)"
            regex2 = "_(" + str(year) + "_american_film)"
            url = title.replace(regex1, "").replace(regex2, "") + "_{}".format(str(year))
         else:
            regex3 = "_(film)"
            url = title.replace(regex3, "")
         urls.append(url) 
         print url
   print len(urls)         
   return urls

def addWords(review, words):
   wc = 0
   for w in review:
      word = w.strip("., \n:;\"-!?[]()/").lower()
      if word in words.keys() and len(word):
         words[word] += 1
      elif len(word):
         words[word] = 1
      else:
         continue
      wc += 1
   return wc

def wordProportion(words, total):
   for k, v in words.items():
      words[k] = float(v)/float(total)

def findDiff(pos_words, neg_words):
   diff_words = {}

   for k, v in pos_words.items():
      if k in neg_words.keys():
         diff_words[k] = float(v) - float(neg_words[k])
      else:
         diff_words[k] = float(v)

   for k, v in neg_words.items():
      if k not in pos_words.keys():
         diff_words[k] = float(v) * -1
   
   return diff_words

urls = getURLs()

print urls

pos_words = {}
neg_words = {}
pos_wc = 0
neg_wc = 0
reviews = []
scores = []

count = 0

for url in urls:
   link = "https://www.rottentomatoes.com/m/{}/reviews/".format(url)
   try:   
      trash, html = commands.getstatusoutput("curl {}".format(link))
      pages = re.findall(r"of ([0-9]*)</span", html)[0]
   except:
      continue
   for page in range(0, int(pages)):
      trash, html = commands.getstatusoutput("curl {}".format(link))
      review = re.findall(r"<div class=\"the_review\"> ([^<]*)</div>", html)
      score = re.findall(r"review_icon icon small ([a-zA-Z]*)", html)
      if len(review) == len(score):
         reviews += review
         scores += score
      link = "https://www.rottentomatoes.com/m/{}/reviews/?page={}&sort=".format(url, str(page + 2))
   count += 1

print "NUMBER OF REVIEWS:", len(reviews)

print "NUMBER OF MOVIES:", count

for i in range(len(reviews)):
   if scores[i] == "fresh":
      pos_wc += addWords(reviews[i].split(), pos_words)
   elif scores[i] == "rotten":
      neg_wc += addWords(reviews[i].split(), neg_words)

print len(pos_words)
print len(neg_words)

wordProportion(pos_words, pos_wc)
wordProportion(neg_words, neg_wc)

diff_words = findDiff(pos_words, neg_words)

for k in sorted(diff_words, key=diff_words.get, reverse=True):
   try:
      os.system("echo {} {} >> diff_words.txt".format(k, diff_words[k]))
   except:
      continue
