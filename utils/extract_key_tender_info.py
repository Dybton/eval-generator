from openai import AsyncOpenAI
from typing import List
import asyncio
import os
import json
from utils.files.read_file import read_file
from pydantic import BaseModel, Field

class TenderInfo(BaseModel):
    solution: List[str] = Field(default_factory=list)
    practical: List[str] = Field(default_factory=list)
    timeline: List[str] = Field(default_factory=list)
    awarding_criteria: List[str] = Field(default_factory=list)
    price: List[str] = Field(default_factory=list)

client = AsyncOpenAI()

async def extract_key_tender_info(tender_content: str) -> TenderInfo:
    system_content = read_file(os.path.join('prompts', 'key_tender_info_en.md'))

    completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user", 
                "content": tender_content
            }
        ]
    )

    response_content = completion.choices[0].message.content
    
    try:
        # Parse the JSON response
        tender_info_dict = json.loads(response_content)
        # Use Pydantic for validation and default values
        return TenderInfo(**tender_info_dict)
    except json.JSONDecodeError:
        print("Warning: Response is not valid JSON")
        print(f"Raw response: {response_content}")
        # Return empty TenderInfo if JSON parsing fails
        return TenderInfo()
    except Exception as e:
        print(f"Error processing response: {str(e)}")
        print(f"Raw response: {response_content}")
        # Return empty TenderInfo on any error
        return TenderInfo()