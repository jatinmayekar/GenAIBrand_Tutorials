import google.generativeai as genai
from IPython.display import Markdown
from dotenv import load_dotenv
load_dotenv()
import os
import tqdm as notebook_tqdm
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# for m in genai.list_models():
#     if "embedContent" in m.supported_generation_methods:
#         print(m.name)

DOCUMENT1 = "Big Basin Hike. big basin state park. ocean view summit. meteor trail. sleeping forest trail. middle ridge trail. People always told me that their favorite hike is in Big Basin, and now I know why!❤️. Lush green!🌲#BigBasinStatePark #HikeCalifornia #TrailLife #ExploreBigBasin #NatureLovers #RedwoodForest #CaliforniaHiking #DiscoverNature #OutdoorAdventure #SantaCruzMountains #HikingCulture #NatureEscape #HikingViews #WanderCalifornia"
DOCUMENT2 = 'Springtime in California means endless blooming hikes! 🌸🌿 The vibrant greens and beautiful views elevate my mood every time. Where should I explore next?#CaliforniaSpring #SpringHikes #HikingCalifornia #NatureLovers #BloomingSeason #ExploreCalifornia #OutdoorAdventure #ScenicTrails #NaturePhotography #GoOutside #vargasplataeu'
DOCUMENT3 = "Zion National Park,Utah.8C, some serious sun burns, a giant human poop (after all it is a scary hike) and what not. Angels Landing!🌌P.S. Angels landed on a very hot day! 😂Also sediments (not sentiments) are my new favourite! 🌚🌝"
DOCUMENT4 = "Rainbow Mt —> Plaza de Armas —> Sacred Valley 🦙🧡#RainbowMountain #Vinicunca #MontanaDeSieteColores #PeruAdventure #IncaTrail #HikingPeru #SacredValley #ValleSagrado #PeruTravel #CuscoRegion #AndeanCulture #IncaHeritage"
DOCUMENT5 = "Hiking through Peruvian Andes- Salkantay Trek to Machu Picchu!🫰🏼❤️😌#SalkantayTrek, #Salkantay, #MachuPicchu, #TrekkingPeru, #AdventureAwaits, #HikingAdventures, #NaturePhotography, #ExplorePeru, #Wanderlust, #TravelDiaries, #EpicViews, #BackpackingPeru, #TrailTales, #OutdoorAdventure. 😂 I made sure everybody knows I wanna see llama and alpaca!"
DOCUMENT6 = "Just a happy kid in havasupai!🥹❤️#havasu #havasufalls #havasupai #mooneyfalls #beaverfalls #supai #backpacking #arizona #grandcanyon. Wow, this permit is really hard to get and I heard the hiking is pretty long. Or there is a helicopter going in once a week do check their cancellation list. ain’t nobody hype me like my main sista!😂 hehe no I am noob!"


documents2 = [DOCUMENT1, DOCUMENT2, DOCUMENT3, DOCUMENT4, DOCUMENT5, DOCUMENT6]

from chromadb import Documents, EmbeddingFunction, Embeddings
from google.api_core import retry

class GeminiEmbeddingFunction(EmbeddingFunction):
    # Specify whether to generate embeddings for documents, or queries
    document_mode = True

    def __call__(self, input: Documents) -> Embeddings:
        if self.document_mode:
            embedding_task = "retrieval_document"
        else:
            embedding_task = "retrieval_query"

        retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}

        response = genai.embed_content(
            model="models/text-embedding-004",
            content=input,
            task_type=embedding_task,
            request_options=retry_policy,
        )
        return response["embedding"]
    
import chromadb

DB_NAME = "googlecardb"
embed_fn = GeminiEmbeddingFunction()
embed_fn.document_mode = True

chroma_client = chromadb.Client()
db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)
db.add(documents=documents2, ids=[str(i) for i in range(len(documents2))])
# print(db.count())

# Switch to query mode when generating embeddings.
embed_fn.document_mode = False

# Search the Chroma DB using the specified query.
query = "Have you ever been to Peru?"

result = db.query(query_texts=[query], n_results=1)
[[passage]] = result["documents"]

#print(passage)

passage_oneline = passage.replace("\n", " ")
query_oneline = query.replace("\n", " ")

# This prompt is where you can specify any guidance on tone, or what topics the model should stick to, or avoid.
prompt = f"""You are a helpful and informative virtual copy of Vasudha that answers questions about Vasudha's instagram on behalf of Vasudha using text from the reference passage included below. 
Be sure to respond in a complete sentence with emojis, copying Vasudha's style using the text from references, being comprehensive, including all relevant background information. 
However, you are talking to audience, who have never travelled to these places and are curios to know, so be sure to break down all the travel checklist and 
strike a friendly and converstional tone. If the passage is irrelevant to the answer, you may ignore it.

QUESTION: {query_oneline}
PASSAGE: {passage_oneline}
"""
print("\nUser 1: " + query_oneline)

model = genai.GenerativeModel("gemini-1.5-flash-latest")
answer = model.generate_content(prompt)
print("\nVasudha: "+answer.text)