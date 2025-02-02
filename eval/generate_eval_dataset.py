from eval.extract_requirements import extract_requirements
from typing import TypedDict, List, Dict

class InputNode(TypedDict):
    text: str
    metadata: Dict[str, str]

class EvalDataset(TypedDict):
    chunk: str
    practical: List[str]
    solution: List[str]
    timeline: List[str]
    awardCriteria: List[str]
    price: List[str]

async def generate_eval_dataset(data: List[InputNode]) -> Dict[str, List[EvalDataset]]:
    eval_dataset: List[EvalDataset] = []
    
    for i, node in enumerate(data):
        print(f"Processing {i + 1}/{len(data)}")
        requirements = await extract_requirements(node["text"])
        eval_dataset.append({
            "chunk": node["text"],
            **requirements
        })
    
    return {"message": "Dataset generated", "data": eval_dataset}