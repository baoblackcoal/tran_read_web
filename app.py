import streamlit as st
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import pandas as pd
from gtts import gTTS
import os
from typing import List, Tuple
import re
import tempfile
from pydub import AudioSegment
import base64
import time
import streamlit.components.v1 as components


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

def has_chinese(text: str) -> bool:
    # Check if the text contains any Chinese character
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

# def read_aloud(text: str) -> None:
#     tts = gTTS(text, lang='zh-cn')
#     tts.save("output.mp3")
    
#     # Read the saved audio file and convert it to bytes
#     with open("output.mp3", "rb") as audio_file:
#         audio_bytes = audio_file.read()
    
#     # Display audio in the browser
#     st.audio(audio_bytes, format='audio/mp3')

def read_aloud(text: str) -> None:
    sentences = re.split(r'(?<=[。？.?\!])\s*', text)
    temp_dir = tempfile.mkdtemp()
    audio_segments = []

    for sentence in sentences:
        try:
            if has_chinese(sentence):
                tts = gTTS(sentence, lang='zh-CN')
            else:
                tts = gTTS(sentence, lang='en')
            
            temp_file = os.path.join(temp_dir, "temp.mp3")
            tts.save(temp_file)
            
            audio_segment = AudioSegment.from_mp3(temp_file)
            audio_segments.append(audio_segment)
        except Exception as e:
            print(f"Error: {e}")        
    
    # Concatenate all audio segments
    combined_audio = AudioSegment.empty()
    for segment in audio_segments:
        combined_audio += segment

    # Save the combined audio to a temporary file
    combined_file = os.path.join(temp_dir, "combined.mp3")
    combined_audio.export(combined_file, format="mp3")

    # Read the combined audio file and convert it to bytes
    with open(combined_file, "rb") as audio_file:
        combined_audio_bytes = audio_file.read()

    # Display the combined audio in the browser using st.audio
    st.audio(combined_audio_bytes, format="audio/mp3")

def remove_bracketed_numbers(text: str) -> str:
    return re.sub(r'\[\d+\]', '', text)

def get_sentences_from_html(html_content: str) -> List[str]:
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')
    sentences = []

    # Improved regular expression to split sentences more accurately
    sentence_splitter = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|！|\!|。|\？)\s|(?<=\.)')

    for para in paragraphs:
        text = para.get_text()
        text = remove_bracketed_numbers(text)  # Remove bracketed numbers
        sentences.extend(sentence_splitter.split(text))

    return sentences

def translate_and_save(sentences: List[str]) -> List[Tuple[str, str]]:
    translations = []
    for sentence in sentences:
        translated_sentence = translate_text(sentence)
        translations.append((sentence, translated_sentence))
    save_to_csv(translations)
    return translations

def on_click_translate() -> None:
    try:
        html_content = fetch_webpage(url)
        paragraphs = get_sentences_from_html(html_content)
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
    if "audio_ended" not in st.session_state:
        st.session_state["audio_ended"] = False

    

    url: str = st.text_input('URL', 'https://en.wikipedia.org/wiki/RIGOL_Technologies')
    content: str = st.session_state.get('content', '')
    init_str = """RIGOL Technologies,  or RIGOL, is a Chinese manufacturer of electronic test equipment.

Rigol Technologies或Rigol是中国电子测试设备的制造商。

 The company has over 500 employees and more than 493 patents.

该公司拥有500多名员工和493多个专利。"""
    if st.session_state.get('content', '') == '':
        st.session_state['content'] = init_str
    content_text_area: str = st.text_area('Content', st.session_state['content'], height=300)
    if st.button('Translate'):
        on_click_translate()

    if st.button('Read'):
        on_click_read()

