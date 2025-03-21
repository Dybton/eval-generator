import os
from dotenv import load_dotenv
from langchain_docling.loader import ExportType
from langchain_docling import DoclingLoader
from docling.chunking import HybridChunker
import json
import uuid
from typing import List, Optional
from pydantic import BaseModel
from utils.types import BoundingBox, DocumentChunk

class Bbox(BaseModel):
    l: float
    t: float
    r: float
    b: float
    coord_origin: str

class Prov(BaseModel):
    page_no: int
    bbox: Bbox
    charspan: List[int]

class DocItem(BaseModel):
    self_ref: str
    parent: dict
    children: List = []
    label: str
    prov: List[Prov]

class Origin(BaseModel):
    mimetype: str
    binary_hash: float
    filename: str

class DlMeta(BaseModel):
    doc_items: List[DocItem]
    headings: List[str]
    origin: Origin

class Metadata(BaseModel):
    source: Optional[str] = None
    dl_meta: DlMeta

class Document(BaseModel):
    id: Optional[int] = None
    metadata: Metadata
    page_content: str
    type: str = "Document"


def docling_parse_and_chunk(file_path):
    load_dotenv()
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    loader = DoclingLoader(
        file_path=[file_path],
        export_type=ExportType.DOC_CHUNKS,
        chunker=HybridChunker()
    )

    docs = loader.load()
    chunks_with_metadata: List[DocumentChunk] = []
    
    for doc in docs:
        
        output_chunk_metadata = DocumentChunk(
            id=str(uuid.uuid4()),
            chunk=doc.page_content,
            page_numbers=[],
            bounding_boxes=[]
        )

        try:
            meta_dict = doc.metadata
            #Check if dl_meta is a string and convert to dict if so with json.loads as the value
            if isinstance(meta_dict.get('dl_meta'), str):
                meta_dict['dl_meta'] = json.loads(meta_dict['dl_meta'])

            metadata_obj = Metadata.model_validate(meta_dict)
            
            # Create a document dict with our expected structure
            doc_dict = Document(
                id=None,
                metadata=metadata_obj,
                page_content=doc.page_content,
                type="Document"
            )
            
            validated_doc = Document.model_validate(doc_dict)
            
            for item in validated_doc.metadata.dl_meta.doc_items:
                for prov in item.prov:
                    page_no = prov.page_no
                    
                    # Create a BoundingBox for output
                    bbox = BoundingBox(
                        left=prov.bbox.l,
                        top=prov.bbox.t,
                        right=prov.bbox.r,
                        bottom=prov.bbox.b,
                        coord_origin=prov.bbox.coord_origin,
                        page=page_no
                    )
                    
                    output_chunk_metadata.bounding_boxes.append(bbox)
                    if page_no not in output_chunk_metadata.page_numbers:
                        output_chunk_metadata.page_numbers.append(page_no)
        
        except Exception as e:
            # Log validation error but keep the chunk with whatever data we have
            print(f"Validation error: {str(e)}")
        
        chunks_with_metadata.append(output_chunk_metadata)

    return chunks_with_metadata