import os
from dotenv import load_dotenv
from langchain_docling.loader import ExportType
from langchain_docling import DoclingLoader
from docling.chunking import HybridChunker
import json
import uuid

# https://ds4sd.github.io/docling/examples/rag_langchain/ - Check this one out for reference

def docling_parse_and_chunk(file_path):
    load_dotenv()
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    EXPORT_TYPE = ExportType.DOC_CHUNKS

    loader = DoclingLoader(
        file_path=[file_path],
        export_type=EXPORT_TYPE,
        chunker=HybridChunker()
    )

    docs = loader.load()

    chunks_with_metadata = []
    
    # Print first few splits with bounding box and page number
    for i, doc in enumerate(docs):
        
        # Initialize the metadata object
        chunk_metadata = {
            "id": str(uuid.uuid4()),
            "text": doc.page_content,
            "page_numbers": [],
            "bounding_boxes": []
        }

        # Extract bounding box and page number from metadata
        if 'dl_meta' in doc.metadata:
            dl_meta = doc.metadata['dl_meta']
            if isinstance(dl_meta, str):
                dl_meta = json.loads(dl_meta)
                
            # Extract all page numbers and bounding boxes from doc_items
            if 'doc_items' in dl_meta and dl_meta['doc_items']:
                for item in dl_meta['doc_items']:
                    if 'prov' in item and item['prov']:
                        for prov in item['prov']:
                            if 'page_no' in prov and 'bbox' in prov:
                                
                                page_no = prov['page_no']
                                bbox = {
                                    'page': page_no,
                                    'coordinates': prov['bbox']
                                }
                                chunk_metadata["bounding_boxes"].append(bbox)
                                if page_no not in chunk_metadata["page_numbers"]:
                                    chunk_metadata["page_numbers"].append(page_no)

        # Add the chunk with its metadata to the list   
        chunks_with_metadata.append(chunk_metadata)

    return chunks_with_metadata

