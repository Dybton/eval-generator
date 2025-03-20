import openai
import numpy as np
import asyncio
from pydantic import BaseModel
from typing import Optional, List
from utils.calculate_cosine import cosine_similarity
from utils.generate_embeddings import generate_embedding

SIMILARITY_THRESHOLD = 0.75

class Insight(BaseModel):
    type: str
    content: str
    chunkId: Optional[str] = None
    embeddings: Optional[List[float]] = None


class EnrichedInsight(Insight):
    embeddings: List[float]


class MatchedInsightPair(BaseModel):
    generated: Insight
    expected: Insight


class EvaluationResult(BaseModel):
    precision: float
    recall: float
    f1_score: float
    extracted_insights_without_match: List[Insight]
    eval_insights_without_match: List[Insight]
    matched_insights: List[MatchedInsightPair]


async def judge_insight_pair(expected: Insight, generated: Insight) -> bool:
    system_content = (
        """
        #### Role
        You are an expert judge comparing two insights. 

        #### Instructions
        - Compare the two insights and respond with 'True' if they represent the same insight, otherwise 'False'.

        ### Return Format
        - Respond with 'True' or 'False'. Do not include any other text.

        """
    )
    user_content = (
        f"Compare these insights:\n"
        f"Expected Insight (type: {expected.type}): {expected.content}\n"
        "Are they the same insight? - Respond with 'True' or 'False'"
    )
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
                "content": user_content
            }
        ]
    )

    result = completion.choices[0].message.content

    if result == "True":
        return True
    elif result == "False":
        return False
    else:
        raise ValueError(f"Invalid response from judge: {result}")


async def evaluate_insights(
    generated_insights: List[Insight],
    expected_insights: List[Insight],
    chunk_by_chunk: bool = False
) -> EvaluationResult:

    enriched_generated_insights = []
    enriched_expected_insights = []

    for insight in generated_insights:
        embedding = generate_embedding(insight.content)
        insight.embeddings = embedding
        enriched_generated_insights.append(insight)

    for insight in expected_insights:
        embedding = generate_embedding(insight.content)
        insight.embeddings = embedding
        enriched_expected_insights.append(insight)

    comparison_pairs = []
    for gen_idx, generated in enumerate(enriched_generated_insights):
        for exp_idx, expected in enumerate(enriched_expected_insights):
            if generated.type != expected.type:
                continue

            if chunk_by_chunk:
                if generated.chunkId != expected.chunkId:
                    continue
                
            if cosine_similarity(generated.embeddings, expected.embeddings) >= SIMILARITY_THRESHOLD:
                comparison_pairs.append((gen_idx, exp_idx, generated, expected))

    extracted_insights_without_match = []
    eval_insights_without_match = []
    true_positive = 0
    matched_insights = []
    
    for gen_idx, exp_idx, generated, expected in comparison_pairs:
        is_match = await judge_insight_pair(generated, expected)
        if is_match:
            true_positive += 1
            matched_insights.append(MatchedInsightPair(generated=generated, expected=expected))
        else:
            extracted_insights_without_match.append(generated)
            eval_insights_without_match.append(expected)

    false_positive = len(extracted_insights_without_match)
    false_negative = len(eval_insights_without_match)

    precision = (true_positive / (true_positive + false_positive)) if (true_positive + false_positive) else 0
    recall = (true_positive / (true_positive + false_negative)) if (true_positive + false_negative) else 0
    f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0



    return EvaluationResult(
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        extracted_insights_without_match=extracted_insights_without_match,
        eval_insights_without_match=eval_insights_without_match,
        matched_insights=matched_insights   
    )

