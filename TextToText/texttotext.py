import streamlit as st
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

bCheckAPIKey = False
bReadyToChat = False
apiKey = ""
assistantResponse = ""

if "bCheckApiKey" not in st.session_state:
    st.session_state.bCheckApiKey = False

if "modelName" not in st.session_state:
    st.session_state.modelName = ""

if "maxTokens" not in st.session_state:
    st.session_state.maxTokens = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "totalCost" not in st.session_state:
    st.session_state.totalCost = 0

st.title("T1: Text to Text")
st.text("By Jatin Mayekar")

#tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['OpenAI', 'Anthropic', 'Meta AI', 'Mistral', 'Hugging Face', 'Groq X'])
tab1, tab2 = st.tabs(['OpenAI', 'Anthropic'])

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
        return response

# OpenAI
with tab1:
    apiKey = st.text_input(label="Enter your API key", type='password', placeholder="sk-...")
    st.write("Find your API key at https://platform.openai.com/account/api-keys")
    if apiKey != "":
        st.session_state.bCheckApiKey = checkApiKey(apiKey)
        
    st.session_state.modelName = st.selectbox(label="Select the model name", options=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o1-mini", "o1-preview"], disabled=not st.session_state.bCheckApiKey)
    st.session_state.maxTokens = st.number_input(label="Enter the max output text length", value=1024, disabled=not st.session_state.bCheckApiKey, min_value=0, max_value=10000000)

    if st.session_state.bCheckApiKey:
        if "client" not in st.session_state:
            st.session_state.client = OpenAI(api_key=apiKey)

for message in st.session_state.messages:
    with st.chat_message(name=message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Hello... how can I help you?", disabled= not st.session_state.bCheckApiKey)
if prompt:
    with st.chat_message(name="user"):
        st.write(prompt)
    with st.chat_message(name="assistant"):
        assistantResponse = getOpenAiResponse(prompt)
        st.write(assistantResponse.choices[0].message.content)
    
    st.session_state.messages.append({"role": "user", "content":prompt})
    st.session_state.messages.append({"role": "assistant", "content":assistantResponse.choices[0].message.content})

    if st.session_state.modelName=="gpt-4o-mini":
        cost_per_prompt_token = 0.00500
        cost_per_completion_token = 0.01500
    elif st.session_state.modelName=="gpt-4o":
        cost_per_prompt_token = 0.000150
        cost_per_completion_token = 0.000600
    elif st.session_state.modelName=="gpt-4-turbo":
        cost_per_prompt_token = 0.0100
        cost_per_completion_token = 0.0300
    elif st.session_state.modelName=="o1-mini":
        cost_per_prompt_token = 0.003
        cost_per_completion_token = 0.012
    elif st.session_state.modelName=="o1-preview":
        cost_per_prompt_token = 0.015
        cost_per_completion_token = 0.060

    with st.expander("Chat Stats"):
        st.write("Chat ID: ", assistantResponse.id)
        st.write("Model: ", assistantResponse.model)
        st.write("Prompt (input) tokens: ", assistantResponse.usage.prompt_tokens)
        st.write("Completion (output) tokens: ", assistantResponse.usage.completion_tokens)
        st.write("Reasoning tokens: ", assistantResponse.usage.completion_tokens_details['reasoning_tokens'])
        st.write("Finish reason: ", assistantResponse.choices[0].finish_reason)
        st.write("Function Calls: ", assistantResponse.choices[0].message.function_call)
        st.write("Tool Calls: ", assistantResponse.choices[0].message.tool_calls)
        currentCost = (assistantResponse.usage.prompt_tokens*cost_per_prompt_token/1000) + (assistantResponse.usage.completion_tokens*cost_per_completion_token/1000)
        st.write("Cost: $ ", currentCost)
        st.session_state.totalCost = st.session_state.totalCost + currentCost
        st.write("Total Cost: $ ", st.session_state.totalCost)
        st.write("See your total api usgae here: https://platform.openai.com/organization/usage")