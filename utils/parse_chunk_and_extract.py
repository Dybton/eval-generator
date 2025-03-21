import asyncio
from typing import List
from utils.docling_parse_and_chunk import docling_parse_and_chunk
from utils.extract_key_tender_info import extract_key_tender_info, TenderInfo
from utils.generate_embeddings import generate_embedding
from utils.types import BoundingBox, DocumentChunk
from pydantic import BaseModel, Field

class EnrichedDocumentChunk(BaseModel):
    id: str 
    chunk: str = Field(default="")
    page_numbers: List[int] = Field(default_factory=list)
    embedding: List[float] = Field(default=[0.0] * 1024)
    bounding_boxes: List[BoundingBox] = Field(default_factory=list)
    extracted_information: TenderInfo = Field(default_factory=TenderInfo)

async def parse_chunk_and_extract(url: str, max_concurrency: int = 5) -> List[EnrichedDocumentChunk]:
    """
    Process a document URL by:
    1. Parsing and chunking the document using docling
    2. Extracting key tender information from each chunk concurrently
    3. Combining the results into enhanced document chunks
    
    Args:
        url: URL or file path to the document to process
        max_concurrency: Maximum number of chunks to process concurrently
        
    Returns:
        List of EnrichedDocumentChunk objects containing both the original chunk data
        and the extracted tender information
    """
    # Step 1: Parse and chunk the document
    print(f"Starting document parsing for: {url}")
    document_chunks = docling_parse_and_chunk(url)
    print(f"Document parsing complete. Found {len(document_chunks)} chunks.")
    
    # Create a pool of max_concurrency workers to process chunks concurrently
    semaphore = asyncio.Semaphore(max_concurrency)
    
    # Create a list of tasks to process the chunks concurrently
    tasks = [
        process_chunk(chunk, i, len(document_chunks), semaphore) 
        for i, chunk in enumerate(document_chunks)
    ]
    
    print(f"Starting extraction of tender information from {len(tasks)} chunks (max {max_concurrency} at a time)...")
    
    # Process chunks concurrently and gather results
    results = await asyncio.gather(*tasks)
    
    # Filter out failed chunks
    successful_results = [
        result for result in results 
        if result is not None
    ]
    
    # Log the number of failed chunks
    failed_count = len(results) - len(successful_results)
    if failed_count > 0:
        print(f"Warning: {failed_count} chunks failed to process properly and were skipped.")
    
    print(f"Processing complete: {len(successful_results)} successful chunks out of {len(results)} total.")
    
    return successful_results

async def process_chunk(chunk: DocumentChunk, index: int, total: int, semaphore: asyncio.Semaphore) -> EnrichedDocumentChunk | None: 
    async with semaphore:
        try:
            print(f"Processing chunk {index+1}/{total} (ID: {chunk.id})")
            tender_info = await extract_key_tender_info(chunk.chunk)
            embedding = await generate_embedding(chunk.chunk)
            print(f"✓ Completed chunk {index+1}/{total} (ID: {chunk.id})")
            
            enriched_chunk = EnrichedDocumentChunk(
                id=chunk.id,
                chunk=chunk.chunk,
                embedding=embedding,
                page_numbers=chunk.page_numbers,
                bounding_boxes=chunk.bounding_boxes,
                extracted_information=tender_info
            )

            validated_chunk = EnrichedDocumentChunk.model_validate(enriched_chunk)
            
            return validated_chunk
        except ValueError as val_err:
            # This will catch Pydantic validation errors
            print(f"Validation error: {str(val_err)}")
            return None
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None
            