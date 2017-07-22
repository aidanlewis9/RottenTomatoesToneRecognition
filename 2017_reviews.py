#!/usr/bin/env python2.7

import os
import sys
import commands
import re

def makeDict(dic, file):
   trash, output = commands.getstatusoutput("cat {}.txt".format(file))
   arr = output.split()
   for i in range(0, len(arr)-1, 2):
      try:
         dic[arr[i]] = float(arr[i+1])
      except:
         continue

def getURLs():
   urls = []
   titles = []
   year = 2017
   yearURL = "https://en.wikipedia.org/wiki/2017_in_film"
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
   return urls

def addWords(review, words):
   score = 0
   for w in review:
      word = w.strip("., \n:;\"-!?[]()/").lower()
      if word in words_dict.keys():
         score += words_dict[word]
   return score

words_dict = {}
urls = getURLs()

fresh_score = 0
fresh_count = 0
rotten_score = 0
rotten_count = 0
reviews = []

makeDict(words_dict, "diff_words")

for url in urls:
   link = "https://www.rottentomatoes.com/m/{}/".format(url)
   try:   
      trash, html = commands.getstatusoutput("curl {}".format(link))
      movie_score = re.findall(r"Average Rating.*span>[^0-9]*([^/]*)/", html)[0]
      link = "https://www.rottentomatoes.com/m/{}/reviews/".format(url)
      trash, html = commands.getstatusoutput("curl {}".format(link))
      pages = re.findall(r"of ([0-9]*)</span", html)[0]
   except:
      continue

   for page in range(0, int(pages)):
      review = re.findall(r"<div class=\"the_review\"> ([^<]*)</div>", html)
      reviews += review
      #print review
      link = "https://www.rottentomatoes.com/m/{}/reviews/?page={}&sort=".format(url, str(page + 2))
      try:   
         trash, html = commands.getstatusoutput("curl {}".format(link))
      except:
         continue

   word_score = 0

   for i in range(len(reviews)):
      word_score += addWords(reviews[i].split(), words_dict)

   if movie_score >= 6:
      fresh_score += word_score
      fresh_count += 1
   else:
      rotten_count += 1
      rotten_score += word_score

   reviews = []

fresh_avg = fresh_score/fresh_count
rotten_avg = rotten_score/rotten_count

print "FRESH Average:", fresh_avg
print "ROTTEN Average:", rotten_avg
