from fastapi import FastAPI, HTTPException, UploadFile, File
import logging
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from utils.docling_parse_and_chunk import docling_parse_and_chunk
from utils.extract_key_tender_info import extract_key_tender_info
from utils.parse_chunk_and_extract import parse_chunk_and_extract
app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/parse-chunk-and-extract")
async def handle_parse_chunk_and_extract(url: str):
    return await parse_chunk_and_extract(url)

# TESTS

@app.get("/docling-parse-and-chunk")
async def handle_docling_parse_and_chunk():
    return docling_parse_and_chunk("https://htzmsmquezyqxwdjmftw.supabase.co/storage/v1/object/public/materials/materials/1741345615581-SERC.pdf")

@app.get("/extract-key-info")
async def handle_extract_key_info():
    return await extract_key_tender_info("I. GENERAL INFORMATION.\nA. Purpose . This request for proposal (RFP) is to contract for legal services to be provided to the State Education Resource Center.\nB. Who May Respond . Attorneys currently licensed to practice law in Connecticut, or law firms including such attorneys, may respond to this RFP.\nC. Instructions on Proposal Submission .\n1. Closing Submission Date . Proposals must be submitted no later than 4:00 pm on August 18, 2017\n2. Inquiries . Inquiries concerning this RFP should be mailed to:\nMichelle Weaver General Counsel State Education Resource Center 100 Roscommon Drive, Suite 110 Middletown, CT 06457\nOr e-mailed to: weaver@ctserc.org\n3. Conditions of Proposal . All costs incurred in the preparation of a proposal responding to this RFP will be the responsibility of the Proposer and will not be reimbursed by the State Education Resource Center (hereinafter referred to as SERC).\n4. Instructions to Prospective Contractors . Your proposal should be addressed as follows:\nMichelle Weaver General Counsel State Education Resource Center 100 Roscommon Drive, Suite 110 Middletown, CT 06457\nIt is important that the proposal be submitted in a sealed envelope clearly marked in the lower left-hand corner with the following information:\nRequest for Proposal 4:00 pm, August 18, 2017\nSEALED PROPOSAL For Legal Services\nFailure to do so may result in premature disclosure of your proposal. It is the responsibility of the Proposer to insure that the proposal is received by SERC, by the date, time and in\n2\nthe manner specified above. Late, unsealed proposals will not be considered.")

