import streamlit as st
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import pandas as pd
from gtts import gTTS
import os
from typing import List, Tuple

# 初始化翻译器
translator = Translator()

def fetch_webpage(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def translate_text(text: str) -> str:
    translated = ''
    try:
        translated = translator.translate(text, src='en', dest='zh-cn').text
    except Exception as e:       
        print(f"Error: {e}")
    return translated

def save_to_csv(data: List[Tuple[str, str]], filename: str = 'translated.csv') -> pd.DataFrame:
    df = pd.DataFrame(data, columns=['Original', 'Translated'])
    df.to_csv(filename, index=False)
    return df

def read_aloud(text: str) -> None:
    tts = gTTS(text, lang='zh-cn')
    tts.save("output.mp3")
    os.system("start output.mp3")

def get_paragraphs(html_content: str) -> List[BeautifulSoup]:
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')
    return paragraphs

def translate_and_save(paragraphs: List[BeautifulSoup]) -> List[Tuple[str, str]]:
    translations = []
    for para in paragraphs:
        original_text = para.get_text()
        translated_text = translate_text(original_text)
        translations.append((original_text, translated_text))
    save_to_csv(translations)
    return translations

def on_click_translate() -> None:
    try:
        html_content = fetch_webpage(url)
        paragraphs = get_paragraphs(html_content)
        translations = translate_and_save(paragraphs)
        combined_text = ''
        for original, translated in translations:
            combined_text += original + '\n\n' + translated + '\n\n'
        st.session_state['content'] = combined_text
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Error: {e}")

def on_click_read() -> None:
    try:
        combined_text = st.session_state.get('content', '')
        read_aloud(combined_text)
    except Exception as e:
        st.error(f"Error: {e}")

# main
if __name__ == '__main__':
    # Streamlit UI
    # st.title('Webpage Translator and Reader')
    url: str = st.text_input('URL', 'https://en.wikipedia.org/wiki/RIGOL_Technologies')
    content: str = st.session_state.get('content', '')
    if st.session_state.get('content', '') == '':
        st.session_state['content'] = 'Test' + '\n\n' + '测试' + '\n\n'
    content_text_area: str = st.text_area('Content', st.session_state['content'], height=300)
    if st.button('Translate'):
        on_click_translate()

    if st.button('Read'):
        on_click_read()
