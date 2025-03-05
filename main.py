from fastapi import FastAPI, HTTPException, UploadFile, File
import logging
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from utils.docling_parse_and_chunk import docling_parse_and_chunk

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/docling-parse-and-chunk")
async def handle_docling_parse_and_chunk():
    return docling_parse_and_chunk("https://ctserc.org/documents/news/2017-07-25-RFP_for%20_legal_SERC_July17.pdf")