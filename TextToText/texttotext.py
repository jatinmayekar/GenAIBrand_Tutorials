import streamlit as st
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

bCheckAPIKey = False
bReadyToChat = False
apiKey = ""

if "bCheckAPIKey" not in st.session_state:
    st.session_state.bCheckAPIKey = False

st.title("T1: Text to Text")
st.text("By Jatin Mayekar")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['OpenAI', 'Anthropic', 'Meta AI', 'Mistral', 'Hugging Face', 'Groq X'])

def checkAPIKey(key):
    try:
        response = client.chat.completions.create(
            messages=[{
                        "role": "user",
                        "content": "Say this is a test",
                    }],
            model="gpt-4o-mini",
        )
        print(response)
        return True
    except openai.AuthenticationError as e:
        st.error("Invalid API key. You can find your API key at https://platform.openai.com/account/api-keys")
        return False

with tab1:
    apiKey = st.text_input(label="Enter your API key", type='password', placeholder="sk-...")
    if apiKey != "":
        client = OpenAI(api_key=apiKey)
        bCheckAPIKey = checkAPIKey(apiKey)
        
    # with st.form("OpenAI"):
    #     if bCheckAPIKey:
    #         st.write("Choose the options and submit to start chatting!")
    modelName = st.selectbox(label="Select the model name", options=["gpt4o-mini", "gpt-4o"], disabled=not bCheckAPIKey)
    maxTokens = st.number_input(label="Enter the max output text length", value=1024, disabled=not bCheckAPIKey, min_value=0, max_value=10000000)

        # bSubmitted = st.form_submit_button(label="Submit", disabled=not bCheckAPIKey)
        # if bSubmitted:
        #     bReadyToChat = True
        #     st.write("Ready to chat!")

prompt = st.chat_input("Hello... how can I help you?", disabled= not bCheckAPIKey)
if prompt:
    with st.chat_message(name="user"):
        st.write(prompt)
    with st.chat_message(name="assistant"):
        st.write("hello")