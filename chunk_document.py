from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser

def chunk_document(markdown_text: str):
    parser = MarkdownNodeParser()
    documents = [Document(text=markdown_text, id_="doc_1")]
    nodes = parser.get_nodes_from_documents(documents)
    return nodes
