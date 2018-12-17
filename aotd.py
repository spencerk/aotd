import requests
from flask import Flask
from bs4 import BeautifulSoup
import _json
from flask import render_template
app = Flask(__name__)




@app.route('/fake')
def aotd():
    term = "English Civil War"
    #proper1 = ["English Civil War", "Emperor Heraclius", "Emperor Khorau", "Persian", "General Rhahzadh", "Mosul", "Iraq"]
    #proper2 = ["England", "Oaks Colliery"]
    #proper3 = ["December Uprising", "Moscow", "Council of Workers' Deputies of Kiev", "Shuliavka Republic"]
    #proper4 = ["Generalissimo Chiang Kai-shek", "Republic of China", "Marshal Zhang Xueliang", "Manchuria"]
    #proper5 = ["Clapham Junction", "London"]

    oldpage = requests.get("https://en.wikipedia.org/wiki/Main_Page", verify=False)

    soup = BeautifulSoup(oldpage.text, 'html.parser')

    soupy= (soup.find('div',{"id": "mp-otd"}))

    soupy1= (soupy.find('ul'))

    lis=soupy1.find_all('li')
    #for elem in lis:
        #records['history'](elem.text.strip())

    #for i in proper1:
    record = {}
    record['history'] = lis[0].text.strip()
    record['searchterm'] = "English Civil War"
    record['reqURL'] = "https://collectionapi.metmuseum.org/public/collection/v1/search?q=%s" % record['searchterm']
    searchReq = requests.get(record['reqURL'])
         
    artObjects = searchReq.json()
    firstObjectID = artObjects["objectIDs"][0]

    objReq = "https://collectionapi.metmuseum.org/public/collection/v1/objects/%s" % firstObjectID
    firstObjectData = requests.get(objReq)

    firstObjectJSON = firstObjectData.json()
    record['img'] = firstObjectJSON['primaryImageSmall']
    record['title'] = firstObjectJSON['title']
    record['artist'] = firstObjectJSON['artistDisplayName']
    record['objURL'] = firstObjectJSON['objectURL']


    return render_template('aotd.html', record=record) 


@app.route('/real')
def aotd_real():


    subscription_key = '02beee7ce5844779b21fa4733308236a'
    assert subscription_key

    text_analytics_base_url = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/"

    key_phrase_api_url = text_analytics_base_url + "entities"
    
    oldpage = requests.get("https://en.wikipedia.org/wiki/Main_Page")
    soup = BeautifulSoup(oldpage.text, 'html.parser')

    soupy= (soup.find('div',{"id": "mp-otd"}))

    soupy1= (soupy.find('ul'))

    lis=soupy1.find_all('li')
    histories = []
    for elem in lis:
        histories.append(elem.text.strip())

    #for i in proper1:
    documents = {'documents' : [
        {'id': '1', 'language': 'en', 'text': histories[0]},
        {'id': '2', 'language': 'en', 'text': histories[1]},
        {'id': '3', 'language': 'en', 'text': histories[2]},
        {'id': '4', 'language': 'en', 'text': histories[3]},
    ]}

    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    response = requests.post(key_phrase_api_url, headers=headers, json=documents)
    key_phrases = response.json()
        
    records = [dict() for x in range(0,4)] 
    for i in range(0,4):
        termCount = len(key_phrases['documents'][i]['entities'])
        records[i]['searchTerms'] = [dict() for x in range(0,termCount)]
        for j in range(0,termCount):
            records[i]['searchTerms'][j]['term'] = (key_phrases['documents'][i]['entities'][j]['name'])

    for i in range(0,4):
        for j in range(0,(len(records[i]['searchTerms']))):
            records[i]['history'] = histories[i]
            records[i]['reqURL'] = "https://collectionapi.metmuseum.org/public/collection/v1/search?q=%s" % records[i]['searchTerms'][j]['term']
            searchReq = requests.get(records[i]['reqURL'])
            artObjects = searchReq.json()
            if artObjects["objectIDs"] is not None:
                firstObjectID = artObjects["objectIDs"][0]
                objReq = "https://collectionapi.metmuseum.org/public/collection/v1/objects/%s" % firstObjectID
                firstObjectData = requests.get(objReq)
                firstObjectJSON = firstObjectData.json()
                if firstObjectJSON['primaryImageSmall'] is not None:
                    records[i]['searchTerms'][j]['img'] = firstObjectJSON['primaryImageSmall']
                    records[i]['searchTerms'][j]['title'] = firstObjectJSON['title']
                    records[i]['searchTerms'][j]['artist'] = firstObjectJSON['artistDisplayName']
                    records[i]['searchTerms'][j]['objURL'] = firstObjectJSON['objectURL']


    return render_template('aotd.html', records=records) 


