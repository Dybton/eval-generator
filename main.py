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

@app.get("/hybrid-chunker")
async def hybrid_chunker():
    try:
        source = "files/1_raw_files/Kontrakt.pdf"  # document per local path or URL

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
    
        chunker = HybridChunker(merge_peers=True, max_tokens=1000)
        chunks = list(chunker.chunk(doc))

        return chunks
    except Exception as e:
        logger.error(f"Error hybrid chunking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/parse-and-chunk-pdf")
async def handle_parse_and_chunk_pdf():
    source = "https://arxiv.org/pdf/2408.09869"
    
    # Configure pipeline options to include images
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = 1
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    result = converter.convert(source)

    chunker = HybridChunker()
    chunk_iter = chunker.chunk(dl_doc=result.document)

    counter = 0

    for i, doc in enumerate(chunk_iter):
        # print(f"\nSplit {i+1}:")
        # print(f"  Content: {doc.page_content}")

        if counter <= 3:
            print(doc)
            counter += 1

    return result

@app.get("/docling-parse-and-chunk")
async def handle_docling_parse_and_chunk():
    return docling_parse_and_chunk("https://ctserc.org/documents/news/2017-07-25-RFP_for%20_legal_SERC_July17.pdf")