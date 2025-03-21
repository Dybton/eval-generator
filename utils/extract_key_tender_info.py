from openai import AsyncOpenAI
from typing import List
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

    completion = await client.chat.completions.create(
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

    if not response_content:
        print("No response content received")
        return TenderInfo()
    
    try:
        # Parse the JSON response
        tender_info_dict = json.loads(response_content)
        
        # Validate with Pydantic and return the model
        tender_info = TenderInfo(**tender_info_dict)
        

        print(f"Successfully validated response with {len(tender_info.solution)} solution items, "
              f"{len(tender_info.practical)} practical items, etc.")
        
        return tender_info
        
    except json.JSONDecodeError as json_err:
        print(f"JSON parsing error: {str(json_err)}")
        print(f"Raw response: {response_content}")
        return TenderInfo()
        
    except ValueError as val_err:
        # This will catch Pydantic validation errors
        print(f"Validation error: {str(val_err)}")
        print(f"Raw response: {response_content}")
        return TenderInfo()
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(f"Raw response: {response_content}")
        return TenderInfo()