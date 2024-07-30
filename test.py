import os
import re
import base64
import tempfile
import time
from gtts import gTTS
from pydub import AudioSegment
import streamlit as st
import streamlit.components.v1 as components

def has_chinese(sentence):
    for ch in sentence:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def read_aloud(text: str) -> None:
    sentences = re.split(r'(?<=[。？.?\!])\s*', text)
    temp_dir = tempfile.mkdtemp()
    audio_segments = []
    
    for sentence in sentences:
        if has_chinese(sentence):
            tts = gTTS(sentence, lang='zh-cn')
        else:
            tts = gTTS(sentence, lang='en')
        
        temp_file = os.path.join(temp_dir, "temp.mp3")
        tts.save(temp_file)

        # Read the saved audio file and convert it to bytes
        with open(temp_file, "rb") as audio_file:
            audio_bytes = audio_file.read()

        # Generate HTML for autoplay audio
        audio_html = f"""
            <audio id="audio-player" autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
            </audio>
            <script>
                var audioPlayer = document.getElementById("audio-player");
                audioPlayer.onended = function() {{
                    var audioEndedEvent = new Event("audio-ended");
                    document.dispatchEvent(audioEndedEvent);
                }};
            </script>
        """
        # Display the audio in the browser
        components.html(audio_html, height=0)

        # JavaScript to set the session state variable when audio ends
        components.html("""
            <script>
                document.addEventListener("audio-ended", function() {
                    window.parent.postMessage({audioEnded: true}, "*");
                });
            </script>
        """, height=0)

        # Wait for the audio to finish playing
        audio_ended = False
        while not audio_ended:
            message = st.experimental_get_query_params().get("message")
            if message and message == "audioEnded":
                audio_ended = True
            time.sleep(0.1)

        audio_segment = AudioSegment.from_mp3(temp_file)
        audio_segments.append(audio_segment)

# Example text to read aloud
text = "Hello. 你好。How are you? 我很好。"

# Read the text aloud
read_aloud(text)
