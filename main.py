from typing import Union
from fastapi import FastAPI, HTTPException, UploadFile, File
import logging
from pathlib import Path
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption
from docling_core.types.doc import PictureItem

from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker import HierarchicalChunker
from docling.chunking import HybridChunker

from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import Document

from save_markdown_with_images import save_markdown_with_images
from parse_document import parse_document
import json


app = FastAPI()
logger = logging.getLogger(__name__)

@app.get("/convert")
async def convert_doc():
    try:

        url = "https://nlsblog.org/wp-content/uploads/2020/06/image-based-pdf-sample.pdf"
        converter = DocumentConverter()
        result = converter.convert(url)
        formatted_markdown = result.document.export_to_markdown()
        
        # Save markdown to testfile.md
        with open("testfile4.md", 'w', encoding='utf-8') as f:
            f.write(formatted_markdown)
            
        return {
            "markdown": formatted_markdown,
            "saved_to": "testfile.md"
        }
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hybrid-chunker")
async def hybrid_chunker():
    try:
        source = "https://arxiv.org/pdf/2408.09869"  # document per local path or URL

        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = 1
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True

        doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        
        result = doc_converter.convert(source)

        doc = result.document
    
        chunker = HybridChunker(include_images=True)
        chunks = list(chunker.chunk(doc))

        print(chunks)

        return chunks
    except Exception as e:
        logger.error(f"Error hybrid chunking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/save-markdown-with-images")
async def save_markdown_w_i():
    try:
        save_markdown_with_images()
    except Exception as e:
        logger.error(f"Error saving markdown with images: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/llama-markdown-parser")
async def parse_it():
    try:
        parsed_nodes = parse_document("exports/tmp5v9wgfpa-with-image-refs.md")
        output = {
            "nodes": [
                {
                    "text": node.text,
                    "metadata": node.metadata
                } for node in parsed_nodes
            ]
        }
        
        with open("chunked_files/parsed_nodes.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
            
        return output
    except Exception as e:
        logger.error(f"Error parsing markdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))