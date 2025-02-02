from docling.document_converter import DocumentConverter

async def parse_document(path: str):
    converter = DocumentConverter()
    result = converter.convert(path)
    formatted_markdown = result.document.export_to_markdown()
    
    return formatted_markdown