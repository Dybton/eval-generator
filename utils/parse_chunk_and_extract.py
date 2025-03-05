import os
import asyncio
from typing import List, TypedDict
from utils.docling_parse_and_chunk import docling_parse_and_chunk, DocumentChunk
from utils.extract_key_tender_info import extract_key_tender_info, TenderInfo

class EnrichedDocumentChunk(TypedDict):
    id: str
    chunk: str
    page_numbers: List[int]
    bounding_boxes: List[dict]
    extracted_information: TenderInfo

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
    
    # Step 2: Extract key tender information from each chunk concurrently
    enhanced_chunks: List[EnrichedDocumentChunk] = []
    
    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def process_chunk(chunk, index, total):
        async with semaphore:  # This limits concurrency
            try:
                print(f"Processing chunk {index+1}/{total} (ID: {chunk['id']})")
                tender_info = await extract_key_tender_info(chunk["chunk"])
                print(f"✓ Completed chunk {index+1}/{total} (ID: {chunk['id']})")
                
                # Create an enhanced document chunk with the extracted information
                enhanced_chunk: EnrichedDocumentChunk = {
                    "id": chunk["id"],
                    "chunk": chunk["chunk"],
                    "page_numbers": chunk["page_numbers"],
                    "bounding_boxes": chunk["bounding_boxes"],
                    "extracted_information": tender_info
                }
                return enhanced_chunk
            except Exception as e:
                print(f"✗ Error processing chunk {index+1}/{total} (ID: {chunk['id']}): {str(e)}")
                # Return a chunk with empty extraction results on error
                return {
                    "id": chunk["id"],
                    "chunk": chunk["chunk"],
                    "page_numbers": chunk["page_numbers"],
                    "bounding_boxes": chunk["bounding_boxes"],
                    "extracted_information": {
                        "solution": [],
                        "practical": [],
                        "timeline": [],
                        "award_criteria": [],
                        "price": []
                    }
                }
    
    # Create tasks for all chunks
    tasks = [
        process_chunk(chunk, i, len(document_chunks)) 
        for i, chunk in enumerate(document_chunks)
    ]
    
    print(f"Starting extraction of tender information from {len(tasks)} chunks (max {max_concurrency} at a time)...")
    # Process chunks concurrently and gather results
    results = await asyncio.gather(*tasks)
    print("All chunks processed successfully!")
    
    return results

# Helper function to run the async function
def process_document(url: str, max_concurrency: int = 5) -> List[EnrichedDocumentChunk]:
    """
    Synchronous wrapper for parse_chunk_and_extract
    
    Args:
        url: URL or file path to the document to process
        max_concurrency: Maximum number of chunks to process concurrently
        
    Returns:
        List of EnrichedDocumentChunk objects
    """
    return asyncio.run(parse_chunk_and_extract(url, max_concurrency))