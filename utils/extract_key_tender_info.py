from openai import AsyncOpenAI
from typing import TypedDict, List, Dict, Any
import asyncio
import os
import json
from utils.files.read_file import read_file

client = AsyncOpenAI()

class TenderInfo(TypedDict):
    solution: List[str]
    practical: List[str]
    timeline: List[str]
    awarding_criteria: List[str]
    price: List[str]

def validate_tender_info(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate that the data adheres to the TenderInfo structure."""
    required_keys = ["solution", "practical", "timeline", "awarding_criteria", "price"]
    
    # Check if all required keys exist
    for key in required_keys:
        if key not in data:
            return False, f"Missing required key: {key}"
        
        # Check if the value is a list
        if not isinstance(data[key], list):
            return False, f"Value for '{key}' is not a list"
        
        # Check if all items in the list are strings
        if not all(isinstance(item, str) for item in data[key]):
            return False, f"Not all items in '{key}' are strings"
    
    # Check for extra keys
    extra_keys = [key for key in data.keys() if key not in required_keys]
    if extra_keys:
        return False, f"Unexpected keys found: {', '.join(extra_keys)}"
    
    return True, ""

async def extract_key_tender_info(tender_content: str) -> TenderInfo:
    system_content = read_file(os.path.join('prompts', 'key_tender_info_en.md'))

    completion = await client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
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
        tender_info = json.loads(response_content)
        
        # Validate the structure
        is_valid, error_message = validate_tender_info(tender_info)
        if not is_valid:
            print(f"Warning: Response does not adhere to expected structure. {error_message}")
            print(f"Non-adhering extraction: {tender_info}")
        
        # Ensure the return value has the correct structure even if validation fails
        result: TenderInfo = {
            "solution": tender_info.get("solution", []),
            "practical": tender_info.get("practical", []),
            "timeline": tender_info.get("timeline", []),
            "awarding_criteria": tender_info.get("awarding_criteria", []),
            "price": tender_info.get("price", [])
        }
        
        return result
    except json.JSONDecodeError:
        print("Warning: Response is not valid JSON")
        print(f"Raw response: {response_content}")
        # Return empty structure if JSON parsing fails
        return {
            "solution": [],
            "practical": [],
            "timeline": [],
            "awarding_criteria": [],
            "price": []
        }