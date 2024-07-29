import streamlit as st
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import pandas as pd
from gtts import gTTS
import os

# 初始化翻译器
translator = Translator()

def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def translate_text(text):
    translated = translator.translate(text, src='en', dest='zh-cn')
    return translated.text

def save_to_csv(data, filename='translated.csv'):
    df = pd.DataFrame(data, columns=['Original', 'Translated'])
    df.to_csv(filename, index=False)
    return df

def read_aloud(text):
    tts = gTTS(text, lang='zh-cn')
    tts.save("output.mp3")
    os.system("start output.mp3")

# get paragraphs from the webpage
def get_paragraphs(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')
    return paragraphs

# translate the text and save to csv
def translate_and_save(paragraphs):
    translations = []
    for para in paragraphs:
        original_text = para.get_text()
        translated_text = translate_text(original_text)
        translations.append((original_text, translated_text))
    df = save_to_csv(translations)
    st.write(df)
    return translations

# on click of the 'Translate' button, fetch the webpage, translate the text, and save to csv
def on_click_translate():
    try:
        html_content = fetch_webpage(url)
        paragraphs = get_paragraphs(html_content)
        translate_and_save(paragraphs)
    except Exception as e:
        st.error(f"Error: {e}")

# on click of the 'Read' button, read the translated text aloud
def on_click_read():
    try:
        df = pd.read_csv('translated.csv')
        combined_text = ' '.join(df['Translated'].tolist())
        read_aloud(combined_text)
    except Exception as e:
        st.error(f"Error: {e}")

# Streamlit UI
st.title('Webpage Translator and Reader')
# url = st.text_input('URL', 'https://en.wikipedia.org/wiki/Wiki')
url = st.text_input('URL', 'https://www.google.com')
if st.button('Translate'):
    on_click_translate()

if st.button('Read'):
    on_click_read()


