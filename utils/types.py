from typing import List
from pydantic import BaseModel

class BoundingBox(BaseModel):
    left: float
    top: float
    right: float
    bottom: float
    coord_origin: str
    page: int

class DocumentChunk(BaseModel):
    id: str
    chunk: str
    page_numbers: List[int]
    bounding_boxes: List[BoundingBox]