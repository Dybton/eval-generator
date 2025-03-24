import openai
from pydantic import BaseModel
from typing import Optional, List, Tuple
from utils.calculate_cosine import cosine_similarity
from utils.generate_embeddings import generate_embedding, generate_embeddings_batch

SIMILARITY_THRESHOLD = 0.65

class Insight(BaseModel):
    type: str
    content: str
    chunk_id: Optional[str] = None
    embeddings: Optional[List[float]] = None

class EnrichedInsight(Insight):
    embeddings: List[float] = []


class InsightPair(BaseModel):
    generated: Insight
    expected: Insight
    similarity_score: float = 0.0


class EvaluationResult(BaseModel):
    precision: float
    recall: float
    extracted_insights_without_match: List[Insight]
    eval_insights_without_match: List[Insight]
    matched_insights: List[InsightPair]
    unmatched_generated_closest_pairs: List[InsightPair] = []
    unmatched_expected_closest_pairs: List[InsightPair] = []

client = openai.AsyncOpenAI()

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
        f"Expected Insight: {expected.content}"
        f"Generated Insight: {generated.content}"
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
    

    # We enrich the insights with embeddings to enable cosine similarity comparison
    enriched_generated_insights = []
    enriched_expected_insights = []

    # Combine the contents of the generated and expected insights
    all_contents = [insight.content for insight in generated_insights + expected_insights]

    # Generate embeddings for all the contents
    all_embeddings = await generate_embeddings_batch(all_contents)
    
    generated_embeddings = all_embeddings[:len(generated_insights)]
    expected_embeddings = all_embeddings[len(generated_insights):]

    # Add the embeddings to the enriched insights
    for i, insight in  enumerate(generated_insights):
        embedding = generated_embeddings[i]
        insight.embeddings = embedding
        enriched_generated_insights.append(insight)

    for i, insight in enumerate(expected_insights):
        embedding = expected_embeddings[i]
        insight.embeddings = embedding
        enriched_expected_insights.append(insight)

    comparison_pairs : List[Tuple[int, int, Insight, Insight, float]] = []

    for gen_idx, generated in enumerate(enriched_generated_insights):
        for exp_idx, expected in enumerate(enriched_expected_insights):

            if generated.type != expected.type:
                continue

            if chunk_by_chunk and (generated.chunk_id != expected.chunk_id):
                continue
                
            similarity_score = cosine_similarity(generated.embeddings, expected.embeddings)

            if similarity_score >= SIMILARITY_THRESHOLD:
                comparison_pairs.append((gen_idx, exp_idx, generated, expected, similarity_score))
            

    matched_insights : List[InsightPair] = []

    matched_generated_indices = set()
    matched_expected_indices = set()
    
    for gen_idx, exp_idx, generated, expected, similarity_score in comparison_pairs:

        is_match = await judge_insight_pair(generated, expected)

        if is_match:
            matched_generated_indices.add(gen_idx)
            matched_expected_indices.add(exp_idx)
            
            matched_insights.append(InsightPair(
                generated=Insight(type=generated.type, content=generated.content, chunk_id=generated.chunk_id),
                expected=Insight(type=expected.type, content=expected.content, chunk_id=expected.chunk_id),
                similarity_score=similarity_score
            ))

    # Find closest match for unmatched insights
    unmatched_generated_closest_pairs = []
    for gen_idx, generated in enumerate(enriched_generated_insights):
        if gen_idx in matched_generated_indices:
            continue
            
        best_score = 0
        closest_expected = None
        
        for expected in enriched_expected_insights:
            if generated.type != expected.type:
                continue
                
            if chunk_by_chunk and (generated.chunk_id != expected.chunk_id):
                continue
                
            similarity_score = cosine_similarity(generated.embeddings, expected.embeddings)
            if similarity_score > best_score:
                best_score = similarity_score
                closest_expected = expected
        
        if closest_expected:
            unmatched_generated_closest_pairs.append(InsightPair(
                generated=Insight(type=generated.type, content=generated.content, chunk_id=generated.chunk_id),
                expected=Insight(type=closest_expected.type, content=closest_expected.content, chunk_id=closest_expected.chunk_id),
                similarity_score=best_score
            ))

    # Find closest match for unmatched expected insights
    unmatched_expected_closest_pairs = []
    for exp_idx, expected in enumerate(enriched_expected_insights):
        if exp_idx in matched_expected_indices:
            continue
            
        best_score = 0
        closest_generated = None
        
        for generated in enriched_generated_insights:
            if expected.type != generated.type:
                continue
                
            if chunk_by_chunk and (expected.chunk_id != generated.chunk_id):
                continue
                
            similarity_score = cosine_similarity(expected.embeddings, generated.embeddings)
            if similarity_score > best_score:
                best_score = similarity_score
                closest_generated = generated
        
        if closest_generated:
            unmatched_expected_closest_pairs.append(InsightPair(
                generated=Insight(type=closest_generated.type, content=closest_generated.content, chunk_id=closest_generated.chunk_id),
                expected=Insight(type=expected.type, content=expected.content, chunk_id=expected.chunk_id),
                similarity_score=best_score
            ))

    # Create clean copies without embeddings for return values
    extracted_insights_without_match = [
        Insight(type=insight.type, content=insight.content, chunk_id=insight.chunk_id)
        for idx, insight in enumerate(enriched_generated_insights)
        if idx not in matched_generated_indices
    ]

    eval_insights_without_match = [
        Insight(type=insight.type, content=insight.content, chunk_id=insight.chunk_id)
        for idx, insight in enumerate(enriched_expected_insights)
        if idx not in matched_expected_indices
    ]
    
    true_positive = len(matched_generated_indices) # How many generated insights are matched to any expected insights
    false_positive = len(enriched_generated_insights) - true_positive # How many generated insights are not matched to any expected insights
    false_negative = len(enriched_expected_insights) - len(matched_expected_indices) # How many expected insights are not matched to any expected insights

    precision = (true_positive / (true_positive + false_positive)) if (true_positive + false_positive) else 0
    recall = (true_positive / (true_positive + false_negative)) if (true_positive + false_negative) else 0

    return EvaluationResult(
        precision=precision,
        recall=recall,
        extracted_insights_without_match=extracted_insights_without_match,
        eval_insights_without_match=eval_insights_without_match,
        matched_insights=matched_insights,
        unmatched_generated_closest_pairs=unmatched_generated_closest_pairs,
        unmatched_expected_closest_pairs=unmatched_expected_closest_pairs
    )

