import streamlit as st
import openai
from openai import OpenAI
import anthropic
import os
from dotenv import load_dotenv
from urllib.error import HTTPError
load_dotenv()

bCheckAPIKey = False
bReadyToChat = False
apiKey = ""
assistantResponse = ""

if "bCheckApiKey" not in st.session_state:
    st.session_state.bCheckApiKey = False

if "tabIndex" not in st.session_state:
    st.session_state.tabIndex = 0

if "modelName" not in st.session_state:
    st.session_state.modelName = ""

if "maxTokens" not in st.session_state:
    st.session_state.maxTokens = 0

if "temperature" not in st.session_state:
    st.session_state.temperature = 0

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
    if st.session_state.tabIndex == 1:
        print("OpenAI")
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
    elif st.session_state.tabIndex == 2:
        print("Anthropic")
        try:
            client = anthropic.Anthropic(api_key=apiKey)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Say this is a test"
                        }
                    ]
                }]
            )
            print(response) #print(response.content[0].text)
            return True 
        except HTTPError as e:
            if e.code == 400:
                st.error("Invalid Request Error. There was an issue with the format or content of your request.")
                return False
            elif e.code == 401:
                st.error("Authentication Error. There's an issue with your API key.")
                return False
            elif e.code == 403:
                st.error("Permission Error. Your API key does not have permission to use the specified resource.")
                return False
            elif e.code == 404:
                st.error("Not Found Error. The requested resource was not found.")
                return False
            elif e.code == 413:
                st.error("Request Too Large. Request exceeds the maximum allowed number of bytes.")
                return False
            elif e.code == 429:
                st.error("Rate Limit Error. Your account has hit a rate limit.")
                return False
            elif e.code == 500:
                st.error("API Error. An unexpected error has occurred internal to Anthropic's systems.")
                return False
            elif e.code == 529:
                st.error("Overloaded Error. Anthropic's API is temporarily overloaded.")
                return False
            else:
                st.error(f"An unexpected error occurred: {e}")
                return False
    else:
        st.error("API key check failed. Try selecting the correct platform and reneter the corret API Key. You can find your API key at https://console.anthropic.com/settings/keys. You can contact the developer at jatinmayekar27@gmail.com")
        print("Wrong tabIndex: ", st.session_state.tabIndex)
    
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

def getAnthropicResponse(prompt):
        response = st.session_state.client.messages.create(
                model=st.session_state.modelName,
                max_tokens=st.session_state.maxTokens,
                temperature=st.session_state.temperature,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ]
                }]
            )
        print(response)
        return response

# OpenAI
with tab1:
    st.session_state.tabIndex = 1
    apiKey = st.text_input(label="Enter your API key", type='password', placeholder="sk-proj...")
    st.write("Find your API key at https://platform.openai.com/account/api-keys")
    if apiKey != "":
        st.session_state.bCheckApiKey = checkApiKey(apiKey)
        
    st.session_state.modelName = st.selectbox(label="Select the model name", options=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o1-mini", "o1-preview"], disabled=not st.session_state.bCheckApiKey)
    st.session_state.maxTokens = st.number_input(label="Enter the max output text length", value=1024, disabled=not st.session_state.bCheckApiKey, min_value=0, max_value=10000000)
    # take number of words as inputs rather than tokens - more intuitive than tokens. 1 token = 0.75 words
    # source: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
    
    if st.session_state.bCheckApiKey:
        if "client" not in st.session_state:
            st.session_state.client = OpenAI(api_key=apiKey)

# Anthropic
with tab2:
    st.session_state.tabIndex = 2
    apiKey = st.text_input(label="Enter your API key", type='password', placeholder="sk-ant...")
    st.write("Find your API key at https://console.anthropic.com/settings/keys")
    if apiKey != "":
        st.session_state.bCheckApiKey = checkApiKey(apiKey)
        
    st.session_state.modelName = st.selectbox(label="Model", options=["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-haiku-20240307", "claude-3-sonnet-20240229"], disabled=not st.session_state.bCheckApiKey)
    st.session_state.temperature = st.number_input(label="Temperature (Higher for creative responses, lower for more predictable responses)", value=0, disabled=not st.session_state.bCheckApiKey, min_value=0, max_value=1)
    st.session_state.maxTokens = st.number_input(label="Max output text length", value=1024, disabled=not st.session_state.bCheckApiKey, min_value=0, max_value=10000000)
    # take nuber of words as inputs rather than tokens - more intuitive than tokens

    if st.session_state.bCheckApiKey:
        if "client" not in st.session_state:
            st.session_state.client = anthropic.Anthropic(api_key=apiKey)

    for message in st.session_state.messages:
        with st.chat_message(name=message["role"]):
            st.write(message["content"])

    input = st.chat_input("Hello... how can I help you?", disabled= not st.session_state.bCheckApiKey)
    if input:
        with st.chat_message(name="user"):
            st.write(input)
        with st.chat_message(name="assistant"):
            if st.session_state.tabIndex == 1:
                assistantResponse = getOpenAiResponse(input)
                output = assistantResponse.choices[0].message.content
            elif st.session_state.tabIndex == 2:
                assistantResponse = getAnthropicResponse(input)
                output = assistantResponse.content[0].text
            st.write(output)

        st.session_state.messages.append({"role": "user", "content":input})
        st.session_state.messages.append({"role": "assistant", "content":output})

        if st.session_state.tabIndex == 1:
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
        elif st.session_state.tabIndex == 2:
            if st.session_state.modelName=="claude-3-5-sonnet-20240620":
                cost_per_input_token = 0.003
                cost_per_output_token = 0.015
            elif st.session_state.modelName=="claude-3-opus-20240229":
                cost_per_input_token = 0.015
                cost_per_output_token = 0.075
            elif st.session_state.modelName=="claude-3-sonnet-20240229":
                cost_per_input_token = 0.003
                cost_per_output_token = 0.015
            elif st.session_state.modelName=="claude-3-haiku-20240307":
                cost_per_input_token = 0.00025
                cost_per_output_token = 0.00125

        with st.expander("Chat Stats"):
            if st.session_state.tabIndex == 1:
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
                st.write("See your total api usage here: https://platform.openai.com/organization/usage")
            elif st.session_state.tabIndex == 2:
                st.write("Chat ID: ", assistantResponse.id)
                st.write("Model: ", assistantResponse.model)
                st.write("Prompt (input) tokens: ", assistantResponse.usage.input_tokens)
                st.write("Completion (output) tokens: ", assistantResponse.usage.output_tokens)
                st.write("Finish/Stop reason: ", assistantResponse.stop_reason)
                st.write("Stop sequence: ", assistantResponse.stop_sequence)
                currentCost = (assistantResponse.usage.input_tokens*cost_per_input_token/1000) + (assistantResponse.usage.output_tokens*cost_per_output_token/1000)
                st.write("Cost: $ ", currentCost)
                st.session_state.totalCost = st.session_state.totalCost + currentCost
                st.write("Total Cost: $ ", st.session_state.totalCost)
                st.write("See your total api usage here: https://console.anthropic.com/settings/usage")