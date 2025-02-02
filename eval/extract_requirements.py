from openai import AsyncOpenAI
from typing import TypedDict, List

class Requirements(TypedDict):
    practical: List[str]
    solution: List[str]
    timeline: List[str]
    awardCriteria: List[str]
    price: List[str]

client = AsyncOpenAI()

async def extract_requirements(text: str) -> Requirements:
    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a detail-oriented tender document analyst. Extract and categorize key information into five distinct sections. Only include information explicitly stated in the text. If no information is found for a category, leave its array empty. Do not add explanatory text or statements about missing information."""
            },
            {
                "role": "user",
                "content": f"""Analyze the following tender document text and provide five arrays of findings. Include ONLY explicitly stated information - if information for a category isn't present, return an empty array.

    1. PRACTICAL REQUIREMENTS (HOW to submit):
    - Document format rules and page limits
    - Legal/licensing prerequisites
    - Submission methods
    - Required certifications
    - Insurance requirements
    - Response format specs
    - Administrative contacts

    2. SOLUTION SPECIFICATIONS (WHAT to deliver):
    - Required deliverables
    - Functionalities
    - Services
    - Technical requirements
    - Performance specs

    3. TIMELINE (all dates/deadlines):
    Format each as 'DATE/PERIOD: ACTION' (max 8 words), chronologically:
    - Submission deadlines
    - Project dates
    - Meeting dates
    - Contract periods
    - Milestones

    4. AWARD CRITERIA:
    - Scoring weights/percentages
    - Technical evaluation criteria
    - Financial evaluation methods
    - Minimum qualifying scores
    - Scoring breakdowns

    5. PRICE INFORMATION:
    // ... existing price info ...

    Text to analyze: {text}

    Format response as JSON with arrays. Leave arrays empty if no relevant information is found:
    {{
    "practical": ["requirement 1", "requirement 2", ...],
    "solution": ["spec 1", "spec 2", ...],
    "timeline": ["date 1: action", "date 2: action", ...],
    "awardCriteria": ["criteria 1", "criteria 2", ...],
    "price": ["price info 1", "price info 2", ...]
    }}"""
            }
        ]
    )

    default_response: Requirements = {
        "practical": [],
        "solution": [],
        "timeline": [],
        "awardCriteria": [],
        "price": []
    }

    try:
        if completion.choices[0].message.content:
            return {**default_response, **eval(completion.choices[0].message.content)}
    except:
        pass
    
    return default_response 