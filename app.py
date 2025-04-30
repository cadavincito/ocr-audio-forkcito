import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

# Configuración de página
st.set_page_config(page_title="OCR con Dark Mode", layout="wide")

# CSS personalizado - Dark Mode
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Tema oscuro principal */
        body {
            background-color: #0f172a;
            color: white !important;
            font-family: 'Poppins', sans-serif;
        }
        .stApp {
            background-color: #1e293b;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Textos en blanco */
        h1, h2, h3, h4, h5, h6, p, label, div, span {
            color: white !important;
        }
        
        /* Sidebar oscuro */
        .stSidebar {
            background-color: #1e293b !important;
            border-right: 1px solid #334155;
        }
        
        /* Radio buttons y checkboxes */
        .stRadio, .stCheckbox {
            color: white !important;
        }
        .stRadio div[role="radiogroup"] label, .stCheckbox label {
            color: white !important;
        }
        
        /* Select boxes */
        .stSelectbox select {
            background-color: #334155;
            color: white;
            border: 1px solid #475569;
        }
        
        /* File uploader */
        .stFileUploader {
            border: 1px solid #475569;
            border-radius: 8px;
            background-color: #334155;
        }
        
        /* Botones */
        .stButton button {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            transition: all 0.3s;
        }
        .stButton button:hover {
            background-color: #2563eb;
        }
        
        /* Text input */
        .stTextInput input {
            background-color: #334155;
            color: white;
            border: 1px solid #475569;
        }
        
        /* Slider */
        .stSlider {
            color: white;
        }
        
        /* Resultados */
        .stAlert {
            background-color: #334155 !important;
            border: 1px solid #475569;
        }
        
        /* Imágenes */
        .stImage {
            border: 1px solid #475569;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

text = " "

def text_to_speech(input_language, output_language, text, tld):
    translator = Translator()
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

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

# Interfaz principal
st.title("Reconocimiento Óptico de Caracteres")
st.subheader("Elige la fuente de la imágen, esta puede venir de la cámara o cargando un archivo")

cam_ = st.checkbox("Usar Cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.subheader("Procesamiento para Cámara")
    filtro = st.radio("Filtro para imagen con cámara", ('Sí', 'No'), index=1)

bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada.', use_column_width=True)
    
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())
    
    st.success(f"Imagen guardada como {uploaded_file.name}")
    img_cv = cv2.imread(f'{uploaded_file.name}')
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

st.write(text)  

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)
    
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb) 
    st.write(text) 

with st.sidebar:
    st.subheader("Parámetros de traducción")
    
    try:
        os.mkdir("temp")
    except:
        pass
    
    translator = Translator()
    
    in_lang = st.selectbox(
        "Seleccione el lenguaje de entrada",
        ("Ingles", "Español", "Bengali", "koreano", "Mandarin", "Japones"),
    )
    if in_lang == "Ingles":
        input_language = "en"
    elif in_lang == "Español":
        input_language = "es"
    elif in_lang == "Bengali":
        input_language = "bn"
    elif in_lang == "koreano":
        input_language = "ko"
    elif in_lang == "Mandarin":
        input_language = "zh-cn"
    elif in_lang == "Japones":
        input_language = "ja"
    
    out_lang = st.selectbox(
        "Select your output language",
        ("Ingles", "Español", "Bengali", "koreano", "Mandarin", "Japones"),
    )
    if out_lang == "Ingles":
        output_language = "en"
    elif out_lang == "Español":
        output_language = "es"
    elif out_lang == "Bengali":
        output_language = "bn"
    elif out_lang == "koreano":
        output_language = "ko"
    elif out_lang == "Chinese":
        output_language = "zh-cn"
    elif out_lang == "Japones":
        output_language = "ja"
    
    english_accent = st.selectbox(
        "Seleccione el acento",
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

    display_output_text = st.checkbox("Mostrar texto")

    if st.button("Convertir"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
    
        if display_output_text:
            st.markdown(f"## Texto de salida:")
            st.write(f" {output_text}")
