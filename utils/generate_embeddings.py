import os
from typing import List
from openai import AsyncOpenAI

# Initialize the OpenAI client with async support
client = AsyncOpenAI()

async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text string using OpenAI's embedding model.
    
    Args:
        text: Text string to generate embedding for
        
    Returns:
        Embedding vector as a list of floats
    """
    try:
        response = await client.embeddings.create(
            
            model="text-embedding-3-large",
            dimensions=1024,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        # Return empty embedding in case of error
        return [0.0] * 1024
