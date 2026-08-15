from pydantic_ai import Agent
from dotenv import load_dotenv
import os
from dataclasses import dataclass
from pydantic_ai.exceptions import ModelAPIError,ModelHTTPError,UnexpectedModelBehavior 

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Gemini API key hasn't been found.")

response_agent = Agent(
    model="google:gemini-3.5-flash-lite",
    instructions="You are a discord thread bot that matches new questions to previously resolved answers."
)
async def get_response(query, memories) -> str:
    """Get response from LLM"""
    try:
        if memories:
            formatted_memories = "\n\n".join(
                [f"--- Past Solution {i+1} ---\n{doc}" for i, doc in enumerate(memories)]
            )
        else:
            formatted_memories = "No relevant past solutions found."
        result = await response_agent.run(f"The post: {query}\nResolved answers from vector db: {formatted_memories}")
        return result.output
    except ModelAPIError as e:
        print(f"Model api error:{e}")
        return "Something wrong with model api and the model couldn't raech it"
    
    except UnexpectedModelBehavior as e:
        print(f"Unexpected model behavior: {e}")
        return "I had trouble generating a response for that."

    except Exception as e:
        print(f"Unhandled error in get_response: {e}")
        return "Something went wrong while processing that."
    
summary_agent = Agent(
    model="groq:llama-3.1-8b-instant",
    instructions="You are a summary agent who will extract question and solution from conversations. And summarize them into short readable description"
)

async def get_summerization(text) -> str:
    """Summarize thread messages into a short readable description."""
    if isinstance(text, list):
        content = "\n".join(str(item) for item in text if item)
    else:
        content = str(text)

    result = await summary_agent.run(content)
    return result.output


query_agent = Agent(
    model="groq:llama-3.3-70b-versatile",
    instructions="""You are a technical search optimizer.
Analyze this Discord forum post and summarize the core technical issue into a single, clean search sentence.
Strip away greetings, filler words, emotional chatter, and unnecessary logs.""",
    
)

async def generate_search_query(question:str) -> str:
    """Generates a search query for vector search"""
    result = await query_agent.run(question)

    return result.output
    