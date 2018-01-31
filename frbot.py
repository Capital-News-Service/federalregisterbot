#pip.main(['install','tweepy'])
#pip.main(['install','requests'])
#pip.main(['install','pandas'])

import tweepy
import requests
import datetime
import pandas as pd
import numpy as np

keys={}
with open("/Users/jagluck/Documents/GitHub/federalregisterbot/keys.json","r") as f:
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
    sendTweet(tweet)
    
def getDate():
    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    print(date)
    return date
    
def getDailyLinks(date):
    params = {'per_page': '1000', 'order' : 'relevance', 'conditions[publication_date][is]': date}
    url = 'https://www.federalregister.gov/api/v1/documents.json'
    r = requests.get(url, params=params)
    return r
    
def getSingleDoc(id):
    url = 'https://www.federalregister.gov/api/v1/documents/' + id + '.json'
    r = requests.get(url)
    return r.json()    
    
date = getDate()
for k in range(10,30):
    date=date[:-2] + str(k)
    i = getDailyLinks(date)
    if (i.json()['count']<=0):
        continue
    results = i.json()['results']
    
    titles = []
    types = []
    abstracts = []
    publication_dates = []
    html_urls = []
    #agencies = []
    
    for j in results:
        #s=getSingleDoc(j['document_number'])
        titles.append(j['title'])
        types.append(j['type'])
        abstracts.append(j['abstract'])
        publication_dates.append(j['publication_date'])
        html_urls.append(j['html_url'])
        
    data = pd.DataFrame(
        {'title': titles,
         'type': types,
         'abstact': abstracts,
         'publication_date' : publication_dates,
         'html_url' : html_urls
        })
    
    data = data.replace(np.nan, '', regex=True)    
    maryland = data[data['abstact'].str.contains("Maryland")]
    
    if (len(maryland) > 0):
        irow = maryland.iterrows()
        for i in irow:
            print(i[1]['title'])
            buildTweet(i[1]['title'],i[1]['html_url'])
    
    
# text = "EPA Final Rule"
# link = "https://www.federalregister.gov/documents/2018/01/29/2018-01518/approval-and-promulgation-of-air-quality-implementation-plans-maryland-nonattainment-new-source"
# buildTweet(text, link)    

    

    
 