import tweepy
import requests
import datetime
import json
import re
from bs4 import BeautifulSoup

def lambda_handler(event, context):
    keys={}
    with open("keys.json","r") as f:
        keys = json.loads(f.read())
    mdterms = []
    with open("mdterms.txt","r") as f:
        mdterms = [i.lower().strip() for i in f.read().strip().split('\n') if len(i)>0 and i[0]!='#' and len(i)>1]
        
    # Consumer keys and access tokens, used for OAuth
    consumer_key = keys["consumer_key"]
    consumer_secret = keys["consumer_secret"]
    access_token = keys["access_token"]
    access_token_secret = keys["access_token_secret"]
    nyt_key = keys["nyt_key"]
     
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

    def getDailyLinks(date):
        params = {'per_page': '1000', 'order' : 'newest', 'conditions[publication_date][is]': date, 'fields[]' :
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

    def daily_kw_search(terms):
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        digest = getDailyLinks(date)
        if (digest.json()['count']<=0):
            return None
        results = digest.json()['results']
        data = []
        for j in digest.json()['results']:
            entry = {'title' : j['title'].encode('ascii','ignore') if j['title']!=None else None,
                'type' : j['type'].encode('ascii','ignore') if j['type']!=None else None,
                'abstract' : j['abstract'].encode('ascii','ignore') if j['abstract']!=None else None,
                'action' : j['action'].encode('ascii','ignore') if j['action']!=None else None,
                'publication_date' : j['publication_date'].encode('ascii','ignore') if j['publication_date']!=None else None,
                'html_url' : j['html_url'].encode('ascii','ignore') if j['html_url']!=None else None,
                'body_html_url' : j['body_html_url'].encode('ascii','ignore') if j['body_html_url']!=None else None,
                'document_number' : j['document_number'].encode('ascii','ignore') if j['document_number']!=None else None,
                'significant' : j['significant'],
                'topic' : j['topics']}
            data.append(entry)
        matched = set()
        for j in range(len(data)):
            if (data[j]['abstract']):
                for term in terms:
                    if (re.search(r"\W"+term+r"\W",data[j]['abstract'].lower())):
                        matched.add(j)
                        break
        if (len(matched) > 0):
            for i in sorted(matched):
                buildTweet(data[i]['title'],data[i]['html_url'])
                print("\n")
        return [data[i] for i in sorted(matched)]
    
    daily_kw_search(mdterms)
    return True
