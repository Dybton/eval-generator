import os
from pathlib import Path
from tempfile import mkdtemp

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_docling.loader import ExportType

from langchain_docling import DoclingLoader

from docling.chunking import HybridChunker

import json
from pathlib import Path
from tempfile import mkdtemp

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus

def docling_langchain_rag():
    load_dotenv()
    # https://github.com/huggingface/transformers/issues/5486:
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    HF_TOKEN = os.getenv("HF_TOKEN")
    FILE_PATH = ["https://arxiv.org/pdf/2408.09869"]  # Docling Technical Report
    EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
    GEN_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    EXPORT_TYPE = ExportType.DOC_CHUNKS
    QUESTION = "Which are the main AI models in Docling?"
    PROMPT = PromptTemplate.from_template(
        "Context information is below.\n---------------------\n{context}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {input}\nAnswer:\n",
    )
    TOP_K = 3
    MILVUS_URI = str(Path(mkdtemp()) / "docling.db")

    print('setup ok')
    print(HF_TOKEN) # What is this token?

    loader = DoclingLoader(
        file_path=FILE_PATH,
        export_type=EXPORT_TYPE,
        chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),
    )

    docs = loader.load()

    if EXPORT_TYPE == ExportType.DOC_CHUNKS:
        splits = docs
    elif EXPORT_TYPE == ExportType.MARKDOWN:
        from langchain_text_splitters import MarkdownHeaderTextSplitter

        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header_1"),
                ("##", "Header_2"),
                ("###", "Header_3"),
            ],
        )
        splits = [split for doc in docs for split in splitter.split_text(doc.page_content)]
    else:
        raise ValueError(f"Unexpected export type: {EXPORT_TYPE}")

    # Print first few splits with bounding box and page number
    for i, doc in enumerate(splits[:12]):
        print(f"\nSplit {i+1}:")
        print(f"  Content: {doc.page_content}")
        
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
                                bbox = prov['bbox']
                                print(f"  Page: {page_no}")
                                print(f"  Bounding Box: {bbox}")
    
    print("...")

    return docs
