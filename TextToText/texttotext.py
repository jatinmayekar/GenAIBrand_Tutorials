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
bPlatformSwitch = False
userModelSelection = ""

if "bCheckApiKey" not in st.session_state:
    st.session_state.bCheckApiKey = False

if "platformChoice" not in st.session_state:
    st.session_state.platformChoice = None

if "oldPlatformChoice" not in st.session_state:
    st.session_state.oldPlatformChoice = None

if "modelName" not in st.session_state:
    st.session_state.modelName = ""

if "maxTokens" not in st.session_state:
    st.session_state.maxTokens = 0

if "maxWords" not in st.session_state:
    st.session_state.maxWords = 0

if "temperature" not in st.session_state:
    st.session_state.temperature = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "totalCost" not in st.session_state:
    st.session_state.totalCost = 0

st.title("T1: Text to Text")
st.text("By Jatin Mayekar")

#tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['OpenAI', 'Anthropic', 'Meta AI', 'Mistral', 'Hugging Face', 'Groq X'])
#tab1, tab2 = st.tabs(['OpenAI', 'Anthropic'])

@st.cache_data
def checkApiKey(apiKey):
    if st.session_state.platformChoice == "OpenAI":
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
    elif st.session_state.platformChoice == "Anthropic":
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

@st.cache_data
def getModelName(modelSelection):
    if modelSelection == "GPT-4o mini (cheap, fast, lightweight tasks such as writing emails, summarizing articles)":
        return "gpt-4o-mini"
    elif modelSelection == "GPT-4o (expensive, complex tasks such as writing research papers, detailed analysis)":
        return "gpt-4o"
    elif modelSelection == "o1-mini (More affordable and quicker than o1-preview, best for help with coding, math, and science, great at STEM subjects.)":
        return "o1-mini"
    elif modelSelection == "o1-preview (Expensive, for solving tough problems in any subject. It's like having a really smart friend who thinks carefully before answering difficult questions about anything)":
        return "o1-preview" 
    elif modelSelection == "Claude 3.5 Sonnet (Most intelligent and most capable, fast and cheaper than opus, use it for complex projects such as researching or analysis)":
        return "claude-3-5-sonnet-20240620" 
    elif modelSelection == "Claude 3 Opus (Intelligent than sonnet 3, most expensive, great for writing and complex tasks)":
        return "claude-3-opus-20240229" 
    elif modelSelection == "Claude 3 Haiku (Fast, cost-effective, great for quick questions and speedy tasks)":
        return "claude-3-haiku-20240307"        

def getOpenAiResponse(prompt):
        response = st.session_state.clientOpenAI.chat.completions.create(
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
        response = st.session_state.clientAnthropic.messages.create(
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

with st.sidebar:
    st.session_state.platformChoice = st.radio(
        "Platform Choice",
        ["OpenAI", "Anthropic"]
    )

    # OpenAI
    if st.session_state.platformChoice == "OpenAI":
        if st.session_state.oldPlatformChoice != st.session_state.platformChoice:
            bPlatformSwitch = True
            st.session_state.oldPlatformChoice = st.session_state.platformChoice
            st.session_state.bCheckApiKey =  False
            st.session_state.messages = []

        with st.popover("Settings"):
            apiKey = st.text_input(label="Enter your API key", type='password', placeholder="sk-proj...")
            st.write("Find your API key at https://platform.openai.com/account/api-keys")
            if apiKey != "":
                st.session_state.bCheckApiKey = checkApiKey(apiKey)
                
            userModelSelection = st.selectbox(label="Model", options=["GPT-4o mini (cheap, fast, lightweight tasks such as writing emails, summarizing articles)", "GPT-4o (expensive, complex tasks such as writing research papers, detailed analysis)", "o1-mini (More affordable and quicker than o1-preview, best for help with coding, math, and science, great at STEM subjects.)", "o1-preview (Expensive, for solving tough problems in any subject. It's like having a really smart friend who thinks carefully before answering difficult questions about anything)"], disabled=not st.session_state.bCheckApiKey)
            st.session_state.modelName = getModelName(userModelSelection)
            st.session_state.maxWords = st.number_input(label="Max word length", value=30, disabled=not st.session_state.bCheckApiKey, min_value=0, max_value=10000000)
            # take number of words as inputs rather than tokens - more intuitive than tokens. 1 token = 0.75 words so 1 word = 1.33 token
            # source: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
            st.session_state.maxTokens = int(st.session_state.maxWords * 0.75) + 20
            
            if st.session_state.bCheckApiKey:
                if "client" not in st.session_state:
                    st.session_state.clientOpenAI = OpenAI(api_key=apiKey)

    # Anthropic
    if st.session_state.platformChoice == "Anthropic":
        if st.session_state.oldPlatformChoice != st.session_state.platformChoice:
            bPlatformSwitch = True
            st.session_state.oldPlatformChoice = st.session_state.platformChoice
            st.session_state.bCheckApiKey =  False
            st.session_state.messages = []

        with st.popover("Settings"):
            apiKey = st.text_input(label="Enter your API key", type='password', placeholder="sk-ant...")
            st.write("Find your API key at https://console.anthropic.com/settings/keys")
            if apiKey != "":
                st.session_state.bCheckApiKey = checkApiKey(apiKey)
                
            userModelSelection = st.selectbox(label="Model", options=["Claude 3.5 Sonnet (Most intelligent and most capable, fast and cheaper than opus, use it for complex projects such as researching or analysis)", "Claude 3 Opus (Intelligent than sonnet 3, most expensive, great for writing and complex tasks)", "Claude 3 Haiku (Fast, cost-effective, great for quick questions and speedy tasks)"], disabled=not st.session_state.bCheckApiKey)
            st.session_state.modelName = getModelName(userModelSelection)
            st.session_state.temperature = st.number_input(label="Creativity Dial (0 to 1 - 0 will get you the most expected answers and deterministic such as typical scientific answers and 1 will get you random, diverse and creative answers such as suggesting a butterfly farm on Mars)", value=0.0, disabled=not st.session_state.bCheckApiKey, min_value=0.0, max_value=1.0, format="%f")
            st.session_state.maxWords = st.number_input(label="Max word length", value=30, disabled=not st.session_state.bCheckApiKey, min_value=0, max_value=10000000)
            st.session_state.maxTokens = int(st.session_state.maxWords * 0.75) + 20

            if st.session_state.bCheckApiKey:
                if "client" not in st.session_state:
                    st.session_state.clientAnthropic = anthropic.Anthropic(api_key=apiKey)

    bChatStats = st.toggle("Show chat statistics")

for message in st.session_state.messages:
    with st.chat_message(name=message["role"]):
        st.write(message["content"])

input = st.chat_input("Hello... how can I help you?", disabled= not st.session_state.bCheckApiKey)
if input:
    with st.chat_message(name="user"):
        st.write(input)
    with st.chat_message(name="assistant"):
        if st.session_state.platformChoice == "OpenAI":
            assistantResponse = getOpenAiResponse(input)
            output = assistantResponse.choices[0].message.content
        elif st.session_state.platformChoice == "Anthropic":
            assistantResponse = getAnthropicResponse(input)
            output = assistantResponse.content[0].text
        st.write(output)

    st.session_state.messages.append({"role": "user", "content":input})
    st.session_state.messages.append({"role": "assistant", "content":output})

    if st.session_state.platformChoice == "OpenAI":
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
    elif st.session_state.platformChoice == "Anthropic":
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

    with st.sidebar:
        with st.expander("Chat Stats"):
            if bChatStats:
                if st.session_state.platformChoice == "OpenAI":
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
                elif st.session_state.platformChoice == "Anthropic":
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