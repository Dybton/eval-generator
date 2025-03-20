import openai
import numpy as np
import asyncio
from pydantic import BaseModel
from typing import Optional, List

# Import the embedding generator from the utility module
from utils.generate_embeddings import generate_embedding

SIMILARITY_THRESHOLD = 0.75

class Insight(BaseModel):
    insight_type: str
    content: str
    chunkId: Optional[str] = None

class EvaluationResult(BaseModel):
    precision: float
    recall: float
    f1_score: float
    extracted_insights_without_match: List[Insight]
    eval_insights_without_match: List[Insight]

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

async def judge_insight_pair(expected: Insight, generated: Insight) -> bool:
    system_content = (
        "You are an expert judge comparing two insights. "
        "Respond with 'yes' if they represent the same insight, otherwise 'no'."
    )
    user_content = (
        f"Compare these insights:\n"
        f"Expected Insight (type: {expected.insight_type}): {expected.content}\n"
        f"Generated Insight (type: {generated.insight_type}): {generated.content}\n"
        "Are they the same insight?"
    )
    completion = await openai.ChatCompletion.acreate(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
    )
    result = completion.choices[0].message.content.strip().lower()
    return "yes" in result

async def evaluate_insights_chunk_by_chunk(
    generated_insights: List[Insight],
    expected_insights: List[Insight]
) -> EvaluationResult:
    generated_embeddings, expected_embeddings = await asyncio.gather(
        asyncio.gather(*(generate_embedding(insight.content) for insight in generated_insights)),
        asyncio.gather(*(generate_embedding(insight.content) for insight in expected_insights))
    )

    matched_generated_indices = set()
    matched_expected_indices = set()
    true_positive = 0

    for exp_index, expected in enumerate(expected_insights):
        exp_embedding = expected_embeddings[exp_index]
        for gen_index, generated in enumerate(generated_insights):
            if gen_index in matched_generated_indices:
                continue
            if generated.insight_type != expected.insight_type:
                continue
            similarity = cosine_similarity(exp_embedding, generated_embeddings[gen_index])
            if similarity >= SIMILARITY_THRESHOLD:
                if await judge_insight_pair(expected, generated):
                    matched_generated_indices.add(gen_index)
                    matched_expected_indices.add(exp_index)
                    true_positive += 1
                    break

    false_positive = len(generated_insights) - len(matched_generated_indices)
    false_negative = len(expected_insights) - len(matched_expected_indices)
    precision = (true_positive / (true_positive + false_positive)) if (true_positive + false_positive) else 0
    recall = (true_positive / (true_positive + false_negative)) if (true_positive + false_negative) else 0
    f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0

    extracted_without_match = [
        generated_insights[i] for i in range(len(generated_insights))
        if i not in matched_generated_indices
    ]
    eval_without_match = [
        expected_insights[i] for i in range(len(expected_insights))
        if i not in matched_expected_indices
    ]

    return EvaluationResult(
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        extracted_insights_without_match=extracted_without_match,
        eval_insights_without_match=eval_without_match
    )




def evaluate_insights_chunk_by_chunk(generated_insights: list[Insight], expected_insights: list[Insight], chunk_by_chunk: bool = False) -> EvaluationResult:

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

    return 
