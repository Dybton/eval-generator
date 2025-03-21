from typing import List
from pydantic import BaseModel

class BoundingBox(BaseModel):
    l: float = 0.0
    t: float = 0.0 
    r: float = 0.0
    b: float = 0.0
    coord_origin: str = "BOTTOMLEFT"
    page: int = 0

class DocumentChunk(BaseModel):
    id: str
    chunk: str
    page_numbers: List[int]
    bounding_boxes: List[BoundingBox] 