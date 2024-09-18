import streamlit as st
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

bCheckAPIKey = False
bReadyToChat = False
apiKey = ""

if "bCheckApiKey" not in st.session_state:
    st.session_state.bCheckApiKey = False

if "modelName" not in st.session_state:
    st.session_state.modelName = ""

if "maxTokens" not in st.session_state:
    st.session_state.maxTokens = 0

st.title("T1: Text to Text")
st.text("By Jatin Mayekar")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['OpenAI', 'Anthropic', 'Meta AI', 'Mistral', 'Hugging Face', 'Groq X'])

@st.cache_data
def checkApiKey(apiKey):
    try:
        client = OpenAI(api_key=apiKey)
        response = client.chat.completions.create(
            messages=[{
                        "role": "user",
                        "content": "Say this is a test",
                    }],
            model="gpt-4o-mini"
        )
        print(response)
        return True
    except openai.AuthenticationError as e:
        st.error("Invalid API key. You can find your API key at https://platform.openai.com/account/api-keys")
        return False
    
def getOpenAiResponse(prompt):
        response = st.session_state.client.chat.completions.create(
            messages=[{
                        "role": "user",
                        "content": prompt,
                    }],
            model=st.session_state.modelName,
            max_tokens=st.session_state.maxTokens
        )
        print(response)
        return response.choices[0].message.content

# OpenAI
with tab1:
    apiKey = st.text_input(label="Enter your API key", type='password', placeholder="sk-...")
    if apiKey != "":
        st.session_state.bCheckApiKey = checkApiKey(apiKey)
        
    st.session_state.modelName = st.selectbox(label="Select the model name", options=["gpt-4o-mini", "gpt-4o"], disabled=not st.session_state.bCheckApiKey)
    st.session_state.maxTokens = st.number_input(label="Enter the max output text length", value=1024, disabled=not st.session_state.bCheckApiKey, min_value=0, max_value=10000000)

    if st.session_state.bCheckApiKey:
        if "client" not in st.session_state:
            st.session_state.client = OpenAI(api_key=apiKey)

prompt = st.chat_input("Hello... how can I help you?", disabled= not st.session_state.bCheckApiKey)
if prompt:
    with st.chat_message(name="user"):
        st.write(prompt)
    with st.chat_message(name="assistant"):
        st.write(getOpenAiResponse(prompt))