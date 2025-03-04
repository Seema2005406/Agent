import os
import datetime
from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from uagents import Agent, Context, Model
from dotenv import load_dotenv

load_dotenv()

class Message(Model):
    message: str

station_agent = Agent(
    name="ChargingStationAgent",
    port=8002,
    seed="station_agent_secret",
    endpoint=["http://127.0.0.1:8002/submit"],
)

def load_vectorstore():
    return Chroma(persist_directory=os.getenv('DB_PATH'), embedding_function=GPT4AllEmbeddings())

def configure_rag_qa():
    vectorstore = load_vectorstore()
    llm = Ollama(model="llama3.2:3b", verbose=True)
    prompt_template = """
        You are a charging station assistant. Your role:
        - Retrieve charging station availability based on system time.
        - Avoid peak rush hours as mentioned in the document.
        - Suggest the best available charging station.
        - Be careful to consider different rush hour offered by different charging stations

        Example:
        Query: Current time is 14:00, find a free charging station avoiding peak hours.
        Response: Charging Station ID 5 is available.

        {context}

        Question: {question}

        Helpful Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
    return qa_chain

rag_chain = configure_rag_qa()

@station_agent.on_event("startup")
async def find_free_station(ctx: Context):
    current_hour = datetime.datetime.now().hour
    query = f"Find a free charging station avoiding peak hours at {current_hour}:00."
    result = rag_chain.invoke(query)
    response = result["result"]
    ctx.logger.info(response)

if __name__ == "__main__":
    station_agent.run()
