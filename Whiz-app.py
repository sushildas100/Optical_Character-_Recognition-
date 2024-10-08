import easyocr as ocr  #OCR
import streamlit as st  #Web App
from PIL import Image #Image Processing
import numpy as np #Image Processing 
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import os
import time
import glob
from gtts import gTTS
from googletrans import Translator
import base64

st.markdown("<h1 style='text-align: center; color: red;'>Whiz Application</h1>", unsafe_allow_html=True)

#st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

st.sidebar.title("Contents")

page_names = ["Image to Text","Text to Speech","Speech Recognition"]
page=st.sidebar.selectbox("Prefer Your Choice",page_names)


if page == 'Image to Text':
    st.subheader("Image to text converter")
    image = st.file_uploader(label = "Upload your image here",type=['png','jpg','jpeg'])
    @st.cache
    def load_model():
        reader = ocr.Reader(['en'],model_storage_directory='.')
        return reader
    reader = load_model() #load model

    if image is not None:
        input_image = Image.open(image) #read image
        st.image(input_image) #display image

        with st.spinner("🤖 AI is at Work! "):
            result = reader.readtext(np.array(input_image))

            result_text = [] #empty list for results
            for text in result:
                result_text.append(text[1])
            st.write(result_text)
        #st.success("Here you go!")
        #st.balloons()
    else:
        st.write("Upload an Image")

if page == "Text to Speech":
    st.subheader("Text to speech")
    try:
        os.mkdir("temp")
    except:
        pass
    translator = Translator()
    text = st.text_input("Enter text")
    in_lang = st.selectbox(
        "Select your input language",
        ("English", "Hindi", "Bengali", "korean", "Chinese", "Japanese"),
    )
    if in_lang == "English":
        input_language = "en"
    elif in_lang == "Hindi":
        input_language = "hi"
    elif in_lang == "Bengali":
        input_language = "bn"
    elif in_lang == "korean":
        input_language = "ko"
    elif in_lang == "Chinese":
        input_language = "zh-cn"
    elif in_lang == "Japanese":
        input_language = "ja"
    
    out_lang = st.selectbox(
        "Select your output language",
        ("English", "Hindi", "Bengali", "korean", "Chinese", "Japanese"),
    )
    if out_lang == "English":
        output_language = "en"
    elif out_lang == "Hindi":
        output_language = "hi"
    elif out_lang == "Bengali":
        output_language = "bn"
    elif out_lang == "korean":
        output_language = "ko"
    elif out_lang == "Chinese":
        output_language = "zh-cn"
    elif out_lang == "Japanese":
        output_language = "ja"
    
    english_accent = st.selectbox(
        "Select your english accent",
        (
            "Default",
            "India",
            "United Kingdom",
            "United States",
            "Canada",
            "Australia",
            "Ireland",
            "South Africa",
        ),
    )
    if english_accent == "Default":
        tld = "com"
    elif english_accent == "India":
        tld = "co.in"

    elif english_accent == "United Kingdom":
        tld = "co.uk"
    elif english_accent == "United States":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "Ireland":
        tld = "ie"
    elif english_accent == "South Africa":
        tld = "co.za"

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Display output text")

    if st.button("convert"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Your audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown(f"## Output text:")
            st.write(f" {output_text}")
    
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)
    remove_files(7)

if page == "Speech Recognition":
    st.header("Speech Recognition")

    stt_button = Button(label="Speak", width=10)

    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
    
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if ( value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
        """))

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0)

    if result:
        if "GET_TEXT" in result:
            st.write(result.get("GET_TEXT"))
