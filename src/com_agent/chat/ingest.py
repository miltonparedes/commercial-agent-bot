from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings

from com_agent.config import settings


def load_information(
    markdown_file_path: str, chunk_size: int = 1000, chunk_overlap: int = 0
) -> None:
    """
    Loads information from a Markdown file, splits it into chunks, and stores it in PGVector.

    Args:
        markdown_file_path (str): Path to the Markdown file to load.
        chunk_size (int): Size of each text chunk. Defaults to 1000.
        chunk_overlap (int): Overlap between chunks. Defaults to 0.

    Returns:
        None
    """
    loader = UnstructuredMarkdownLoader(markdown_file_path)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    split_texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    PGVector.from_documents(
        documents=split_texts,
        embedding=embeddings,
        connection_string=settings.DATABASE_URL,
        collection_name="company_info",
    )

    print("Company information successfully loaded into PGVector.")
