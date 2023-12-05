# import libraries
from bs4 import BeautifulSoup
import re
from bs4.dammit import EncodingDetector
import requests
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
import matplotlib.pyplot as plt 
from PIL import Image
from os import path, getcwd
import numpy as np

import nltk
nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# scrape data from web page
def get_soup(html):
    resp = requests.get(html)
    # if charset is in headers of content-type, convert charset into lowercase, else don't include it
    http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
    encoding = html_encoding or http_encoding
    soup = BeautifulSoup(resp.content, from_encoding=encoding, features="lxml")
    return soup

# get list of links from web page
def get_links(soup):
    link_list = []
    # find all links including 'bpp', which indicates they are a link to a podcast transcript. All other links are not relavent 
    for link in soup.find_all(href=re.compile("bpp")):
        # remove links in the website that are not relavent to us, which begin with '/'
        if link['href'][0] != '/':
            link_list.append(link['href'].strip("'"))
    return link_list

# get <p> tags from webpage, they contain transcribed podcast
def get_ps(soup):
    http_link_list = []
    for link in soup.find_all('p'):
        http_link_list.append(link.get_text())
    return http_link_list

# extract text from link
def get_text(text_array):
    """ get text from an array"""
    text = " ".join(text_array)
    return text

# extract text from all episodes in list
def get_episode_text(episode_list):
    text_ret = []
    for i in episode_list:
        print(i)
        soup = get_soup(i)
        text_array = get_ps(soup)
        full_text = get_text(text_array)
        text_ret.append(full_text)
    return text_ret

# filter out punctuation and stop words
# A stop word is a commonly used word (such as “the”, “a”, “an”, “in”) that a search engine has been programmed to ignore
def punctuation_stop(text):
    filtered = []
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    for w in word_tokens:
        if w not in stop_words and w.isalpha(): #isalpha ensures we are only looking at text
            filtered.append(w.lower())
    return filtered

# webpage URL
bp_transcripts = 'https://www.biggerpockets.com/podcast-transcripts'

soupout = get_soup(bp_transcripts)

# get list of links
h_links = get_links(soupout)

# return list of all episode text
text_return_list = get_episode_text(h_links)
all_text = get_text(text_return_list)

#removed punctuation and stop words
filtred_list = punctuation_stop(all_text)

#list of unwanted words 
unwanted = ['brandon','josh','one','guy','really','mean','little bit','thing','say','go','actually','even','probably','going','said','something','okay','maybe','got','well','way']

# create new text object that only contains relevant words 
text = " ".join([ele for ele in filtred_list if ele not in unwanted])

# get the working directory    
d = getcwd()

# numpy image file of mask image. Image.open from PIL package
mask_logo = np.array(Image.open(path.join(d, "Bigger_Pockets_Logo4.png")))

# create wordcloud object
wc = WordCloud(background_color="white", max_words=2000, max_font_size=90, random_state=1, mask=mask_logo, stopwords=STOPWORDS)

wc.generate(text)

image_colors = ImageColorGenerator(mask_logo)

# plot figure using matplotlib
plt.figure(figsize=[10,10])
plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
plt.axis('off')
plt.show()