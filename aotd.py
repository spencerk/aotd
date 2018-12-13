import requests
from flask import Flask
from bs4 import BeautifulSoup
import _json
from flask import render_template
app = Flask(__name__)

@app.route('/')
def aotd():
    return render_template('aotd.html')
