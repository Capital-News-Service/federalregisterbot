#pip.main(['install','tweepy'])
#pip.main(['install','requests'])
#pip.main(['install','pandas'])
#pip.main(['install','beautifulsoup4'])

import tweepy
import requests
import datetime
import pandas as pd
import numpy as np
import json
import re
import math
from bs4 import BeautifulSoup
import nltk
import string
from collections import Counter
from nltk.corpus import stopwords


keys={}
with open("keys.json","r") as f:
    keys = json.loads(f.read())
    
# Consumer keys and access tokens, used for OAuth
consumer_key = keys["consumer_key"]
consumer_secret = keys["consumer_secret"]
access_token = keys["access_token"]
access_token_secret = keys["access_token_secret"]
 
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth)

def sendTweet(content):
    api.update_status(content)
    
def buildTweet(text, link):
    tweet = text + " " + link
    #sendTweet(tweet)
    
def getDate():
    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    return date
    
def getDailyLinks(date):
    params = {'per_page': '1000', 'order' : 'relevance', 'conditions[publication_date][is]': date, 'fields[]' :
        ["abstract",
        "action",
        "agencies",
        "body_html_url",
        "html_url",
        "document_number",
        "significant",
        "topics",
        "type",
        "title",
        "publication_date"]
    }
    url = 'https://www.federalregister.gov/api/v1/documents.json'
    r = requests.get(url, params=params)
    return r
    
def getSingleDoc(id):
    url = 'https://www.federalregister.gov/api/v1/documents/' + id + '.json'
    r = requests.get(url)
    return r.json()   
    
def getFullText(url):
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data,"html.parser")
    return soup
        
def getKeywordStats(days):
    base = datetime.datetime.today()
    data = []
    for k in [base - datetime.timedelta(days=x) for x in range(0, days)]:
        date = k.strftime('%Y-%m-%d')
        digest = getDailyLinks(date)
        if (digest.json()['count'] == 0):
            continue

        for j in digest.json()['results']:
            entry = {'title' : j['title'],
                'type' : j['type'],
                'abstract' : j['abstract'],
                'action' : j['action'],
                'publication_date' : j['publication_date'],
                'html_url' : j['html_url'],
                'body_html_url' : j['body_html_url'],
                'document_number' : j['document_number'],
                'significant' : j['significant'],
                'topic' : j['topics']}
            data.append(entry)
    #print len(data)
    # for entry in data:
    #     if (entry['abstract'] != None):
    #         abstract = entry['abstract'].encode('ascii','ignore').lower().translate(None, string.punctuation)
    #         # for i in re.findall('(?:(?<!The\s)(?:[A-Z][\w\-\[\]\.]*\w,?\s|U\.S\.\s|Mr\.\s|Ms\.\s|\Mrs\.\s)(?:[A-Z][\w\-\[\]\.]+\w,?\s|and\s|the\s|for\s|of\s)*(?:[A-Z][\w\-\[\]\.,]+\w|\d+))|(?:http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)|(?:[\w\-\[\]\.]+\w)',abstract):
    #         for i in re.findall('[\w\-\[\]\.]+\w',abstract):
    #             if not(i in stats['abstract_keywords']):
    #                 stats['abstract_keywords'][i] = 1
    #             else:
    #                 stats['abstract_keywords'][i] += 1
    # max_size = max([len(i) for i in stats['abstract_keywords'].keys()])
    # with open() as k:
    #     for key, value in sorted(stats['abstract_keywords'].iteritems(), key=lambda (k,v): (-1*v,k)):
    #         print "%-20s  %-3s" % (key[:20],str(value)
    abstracts = {}
    c=1
    for entry in data:
        if (entry['abstract'] != None):
            abstract = entry['abstract'].encode('ascii','ignore').lower().translate(None, string.punctuation)
            tokens = nltk.word_tokenize(abstract)
            filtered = [w for w in tokens if not w in stopwords.words('english')]
            regex = re.compile('[0-9]')
            filtered = [ i for i in filtered if not(regex.search(i))]
            if (entry['title'] != None):
                abstracts[entry['title'].encode('ascii','ignore')] = filtered
            else:
                abstracts['Untitled '+str(c)] = filtered
                c+=1
    # use only one of the following lines, whichever you prefer
    idf = {}
    tf = {}
    print abstracts
    for k,v in abstracts.iteritems():
        tf[k] = {}
        for i in v:
            if (i in tf[k].keys()):
                tf[k][i] += 1
            else:
                tf[k][i] = 1
            if (i in idf.keys()):
                idf[i] += 1
            else:
                idf[i] = 1
    ndf=len(abstracts)
    for k,v in idf.iteritems():
        idf[k] = math.log(ndf*1.0/v)
    print idf
    for k,v in tf.iteritems():
        dl=len(tf[k])
        for k1,v1 in tf[k].iteritems():
            tf[k][k1]*=(idf[k1]*1.0/dl)
        print k
        print [i[0] for i in sorted(tf[k].iteritems(), key=lambda (k,v): (-1*v,k))[:6]]
        print





def filter():
    numdays = 60
    base = datetime.datetime.today()
    for k in [base - datetime.timedelta(days=x) for x in range(0, numdays)]:
        #date="2018-01-" + str(k)
        date = k.strftime('%Y-%m-%d')
        i = getDailyLinks(date)
        if (i.json()['count']<=0):
            continue
        results = i.json()['results']
        
        titles = []
        types = []
        abstracts = []
        publication_dates = []
        html_urls = []
        body_html_urls = []
        document_numbers = []
        actions = []
        significants = []
        topics = []
        #agencies = []
        
        for j in results:
            #s=getSingleDoc(j['document_number'])
            titles.append(j['title'])
            types.append(j['type'])
            abstracts.append(j['abstract'])
            publication_dates.append(j['publication_date'])
            html_urls.append(j['html_url'])
            body_html_urls.append(j['body_html_url'])
            document_numbers.append(j['document_number'])
            actions.append(j['action'])
            significants.append(j['significant'])
            topics.append(j['topics'])
            
        data = pd.DataFrame(
            {'title': titles,
             'type': types,
             'abstact': abstracts,
             'publication_date' : publication_dates,
             'html_url' : html_urls,
             'document_number' : document_numbers,
             'action' : actions,
             'significant' : significants,
             'topic' : topics,
             'body_html_url' : body_html_urls
            })
        
        data = data.replace(np.nan, '', regex=True)    
        maryland = data[data['abstact'].str.contains("Maryland")]
        
        if (len(maryland) > 0):
            irow = maryland.iterrows()
            for i in irow:
                print(i[1]['title'])
                print(i[1]['publication_date'])
                buildTweet(i[1]['title'],i[1]['html_url'])
                text = getFullText(i[1]['body_html_url'])
                #print(text)
                print("\n")

getKeywordStats(20)
# text = "EPA Final Rule"
# link = "https://www.federalregister.gov/documents/2018/01/29/2018-01518/approval-and-promulgation-of-air-quality-implementation-plans-maryland-nonattainment-new-source"
# buildTweet(text, link)   
