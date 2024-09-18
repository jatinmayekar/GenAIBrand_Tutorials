import streamlit as st
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

bCheckAPIKey = False
apiKey = ""

if "bCheckAPIKey" not in st.session_state:
    st.session_state.bCheckAPIKey = False

st.title("T1: Text to Text")
st.text("By Jatin Mayekar")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['OpenAI', 'Anthropic', 'Meta AI', 'Mistral', 'Hugging Face', 'Groq X'])

def checkAPIKey(key):
    if key=="openai":
        return True
    else:
        return False

with tab1:
    apiKey = st.text_input(label="Enter your API key", type='password', placeholder="OPENAIAPIKEY")
    if apiKey != "":
        bCheckAPIKey = checkAPIKey(apiKey)
        if bCheckAPIKey:
            st.text("API Key is valid")
        else:
            st.text("API Key is invalid. Enter again")
        
    with st.form("OpenAI"):
        modelName = st.selectbox(label="Select the model name", options=["gpt4o-mini", "gpt-4o"], disabled=not bCheckAPIKey)
        maxTokens = st.text_input(label="Enter the max output length", placeholder="1024", disabled=not bCheckAPIKey)

        bSubmitted = st.form_submit_button(label="Submit", disabled=not bCheckAPIKey)
        #bSubmitted = st.form_submit_button(label="Submit")

        if bSubmitted:
            st.write("Ready to chat!")