import requests
from flask import Flask
from bs4 import BeautifulSoup
import _json
from flask import render_template
import random
import logging
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
cache = SimpleCache()

def add_records():
    # Connect to Azure
    subscription_key = '02beee7ce5844779b21fa4733308236a'
    assert subscription_key

    text_analytics_base_url = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/"
    key_phrase_api_url = text_analytics_base_url + "entities"
    
    # Scrape wikipedia main page
    wiki_main = requests.get("https://en.wikipedia.org/wiki/Main_Page", verify=False)
    soup = BeautifulSoup(wiki_main.text, 'html.parser')
    onThisDay = soup.find('div',{"id": "mp-otd"}).find('ul')
    occurrences = onThisDay.find_all('li')

    # Mine scraped occurences for this day's events
    documents = {'documents' : []}
    for idx, val in enumerate(occurrences):
        documents['documents'].append({'id': idx,'language': 'en','text': val.text.strip()})

    # Send to Azure to get key phrases
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    response = requests.post(key_phrase_api_url, headers=headers, json=documents)
    key_phrases = response.json()
        
    # Create a place to store records to display    
    records = [dict() for x in range(0,len(occurrences))] 

    # Append search terms and data to records     
    for i in range(0,len(occurrences)): # for each occurrence i in occurrences
        terms = key_phrases['documents'][i]['entities']
        #print terms
        termCount = len(terms)
        records[i]['history'] = occurrences[i].text #add historical data
        records[i]['searchTerms'] = []
        for j in range(0,termCount): # for each term j in termcount
            if key_phrases['documents'][i]['entities'][j]['name'] is not None:
                # Loop through each term in each event and add data
                searchTerm = (key_phrases['documents'][i]['entities'][j]['name'])
                searchRequestURL =  "https://collectionapi.metmuseum.org/public/collection/v1/search?q=%s" % searchTerm 
                searchReq = requests.get(searchRequestURL) #search for objects based on search term
                artObjects = searchReq.json()
                if artObjects["objectIDs"] is not None:
                    firstObjectID = artObjects["objectIDs"][0]
                    objReq = "https://collectionapi.metmuseum.org/public/collection/v1/objects/%s" % firstObjectID
                    firstObjectData = requests.get(objReq)
                    firstObjectJSON = firstObjectData.json()
                        
                    if firstObjectJSON['primaryImageSmall'] != "" :
                        #build the record only if the search result returned something that has an image
                            info = {
                                    "term":     searchTerm,
                                    "reqURL":   searchRequestURL,
                                    "img":      firstObjectJSON['primaryImageSmall'],
                                    "title":    firstObjectJSON['title'],
                                    "artist":   firstObjectJSON['artistDisplayName']
                                    }
                            records[i]['searchTerms'].append(info)

    for r in range(0,len(records)-1):
        if len(records[r]['searchTerms']) == 0:
            records.remove(r)

    return records

def get_rand_record(rec):
    recCount = len(rec)-1
    randRecord = rec[random.randint(0,recCount-1)]
    return randRecord

def get_records():
    rv = cache.get('my_records')
    if rv is None:
        rv = add_records()
        cache.set('my_records', rv, timeout=5 * 60)
    return rv

@app.route('/today')
def aotd():

    rec = get_records()
    randRecord = get_rand_record(rec)
    terms = randRecord['searchTerms']   
    randTerm = terms[random.randint(0,len(terms)-1)]

    hist = randRecord['history']
    return render_template('aotd.html', history=hist, term=randTerm) 


