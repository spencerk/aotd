import requests
from flask import Flask
from bs4 import BeautifulSoup
import _json

records=[]
proper1 = ["Byzantine", "Emperor Heraclius", "Emperor Khorau", "Persian", "General Rhahzadh", "Mosul", "Iraq"]
proper2 = ["England", "Oaks Colliery"]
proper3 = ["December Uprising", "Moscow", "Council of Workers' Deputies of Kiev", "Shuliavka Republic"]
proper4 = ["Generalissimo Chiang Kai-shek", "Republic of China", "Marshal Zhang Xueliang", "Manchuria"]
proper5 = ["Clapham Junction", "London"]

oldpage = requests.get("https://en.wikipedia.org/wiki/Main_Page")

soup = BeautifulSoup(oldpage.text, 'html.parser')

soupy= (soup.find('div',{"id": "mp-otd"}))

soupy1= (soupy.find('ul'))

lis=soupy1.find_all('li')
for elem in lis:
    records.append(elem.text.strip())

print (records)

print ("********")

for i in proper1:
    searchterm = i
    newpage = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/search?q="+searchterm)

    print (newpage.text)

newstuff = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/objects/470268")

print (newstuff.text)


# https://www.metmuseum.org/art/collection/search/464489

roar = requests.get("http://popularity.csail.mit.edu/cgi-bin/image.py?url=https://en.wikipedia.org/wiki/Horse#/media/File:Nokota_Horses_cropped.jpg")
print (roar.text)

f = open('aotd.html','w')

message = """<html>
<head></head>
<body>
Artwork of the Day

</body>
</html>"""

f.write(message)
f.close()


