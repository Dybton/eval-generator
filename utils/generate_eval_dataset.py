from eval.extract_requirements import extract_requirements
from typing import TypedDict, List, Dict
import asyncio

class InputNode(TypedDict):
    text: str
    metadata: Dict[str, str]

class EvalDataset(TypedDict):
    chunk: str
    practical: List[str]
    solution: List[str]
    timeline: List[str]
    award_criteria: List[str]
    price: List[str]

async def generate_eval_dataset(data: List[InputNode], language: str) -> Dict[str, List[EvalDataset]]:
    semaphore = asyncio.Semaphore(5)

    async def process_node(node: InputNode, index: int) -> EvalDataset:
        async with semaphore:
            print(f"Processing {index + 1}/{len(data)}")
            requirements = await extract_requirements(node["text"], language)
            return {
                "chunk": node["text"],
                **requirements
            }

    tasks = [asyncio.create_task(process_node(node, i)) for i, node in enumerate(data)]

    results = await asyncio.gather(*tasks)

    return {"message": "Dataset generated", "data": results}