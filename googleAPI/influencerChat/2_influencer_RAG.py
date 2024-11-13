import streamlit as st
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
from google.api_core import retry
import chromadb
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Sample Instagram posts - In production, you would load these from a database
DOCUMENTS = [
    "hi, I am VL, Digital creator, Documenting self discovery & everything that brings me joy!🌻"
    "Big Basin Hike. big basin state park. ocean view summit. meteor trail. sleeping forest trail. middle ridge trail. People always told me that their favorite hike is in Big Basin, and now I know why!❤️. Lush green!🌲#BigBasinStatePark #HikeCalifornia #TrailLife #ExploreBigBasin",
    'Springtime in California means endless blooming hikes! 🌸🌿 The vibrant greens and beautiful views elevate my mood every time. Where should I explore next?#CaliforniaSpring #SpringHikes #HikingCalifornia',
    "Zion National Park,Utah.8C, some serious sun burns, a giant human poop (after all it is a scary hike) and what not. Angels Landing!🌌",
    "Rainbow Mt —> Plaza de Armas —> Sacred Valley 🦙🧡#RainbowMountain #Vinicunca #MontanaDeSieteColores #PeruAdventure",
    "Hiking through Peruvian Andes- Salkantay Trek to Machu Picchu!🫰🏼❤️😌#SalkantayTrek, #Salkantay, #MachuPicchu, #TrekkingPeru",
    "Just a happy kid in havasupai!🥹❤️#havasu #havasufalls #havasupai #mooneyfalls #beaverfalls #supai #backpacking #arizona #grandcanyon"
]

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.document_mode = True

    def __call__(self, input: Documents) -> Embeddings:
        embedding_task = "retrieval_document" if self.document_mode else "retrieval_query"
        retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}
        
        response = genai.embed_content(
            model="models/text-embedding-004",
            content=input,
            task_type=embedding_task,
            request_options=retry_policy,
        )
        return response["embedding"]

def initialize_rag():
    embed_fn = GeminiEmbeddingFunction()
    chroma_client = chromadb.Client()
    db = chroma_client.get_or_create_collection(name="instagram_db", embedding_function=embed_fn)
    
    # Add documents if collection is empty
    if db.count() == 0:
        db.add(documents=DOCUMENTS, ids=[str(i) for i in range(len(DOCUMENTS))])
    return db, embed_fn

def get_rag_response(query, db, embed_fn):
    # Set to query mode for searching
    embed_fn.document_mode = False
    
    # Search the database
    result = db.query(query_texts=[query], n_results=1)
    [[passage]] = result["documents"]
    
    # Format the prompt
    passage_oneline = passage.replace("\n", " ")
    query_oneline = query.replace("\n", " ")
    
    prompt = f"""You are a helpful and informative virtual copy of Vasudha that answers questions about Vasudha's instagram on behalf of Vasudha using text from the reference passage included below. 
    Be sure to respond in a complete sentence with emojis, copying Vasudha's style using the text with emojis from references, being comprehensive, including all relevant background information. 
    However, you are talking to audience who have never travelled to these places and are curious to know, so be sure to break down all the travel checklist and 
    strike a friendly and conversational tone. If the passage is irrelevant to the answer, you may ignore it.

    QUESTION: {query_oneline}
    PASSAGE: {passage_oneline}
    """
    
    # Generate response using Gemini
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    return response.text

# Streamlit Interface
st.title("Chat with Vasudha - Travel Influencer 🌎")
st.markdown("Ask me anything about my travels and adventures! 🎒✈️")

# Initialize session state for messages if not exists
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize RAG system
if "rag_system" not in st.session_state:
    db, embed_fn = initialize_rag()
    st.session_state.rag_system = {"db": db, "embed_fn": embed_fn}

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle user input
if prompt := st.chat_input("Ask about my travels..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_rag_response(
                prompt, 
                st.session_state.rag_system["db"],
                st.session_state.rag_system["embed_fn"]
            )
            st.write(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Add a sidebar with information about the influencer
with st.sidebar:
    st.image("https://via.placeholder.com/150", caption="Vasudha")
    st.markdown("### About Me")
    st.write("Travel enthusiast exploring the world! 🌎 Sharing my adventures and travel tips with you all! ✈️")
    st.markdown("### Featured Destinations")
    st.write("- 🏔️ Big Basin State Park")
    st.write("- 🏜️ Zion National Park")
    st.write("- 🗻 Machu Picchu")
    st.write("- 💦 Havasu Falls")