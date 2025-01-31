from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser

def parse_document(path: str):
    with open(path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    parser = MarkdownNodeParser()
    documents = [Document(text=markdown_text, id_="doc_1")]

    nodes = parser.get_nodes_from_documents(documents)

    for node in nodes:
        print(node)

    return nodes
