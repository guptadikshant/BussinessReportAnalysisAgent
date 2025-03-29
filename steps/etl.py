from langchain_core.documents import Document
from loguru import logger
from typing_extensions import Annotated
from zenml import get_step_context, step

from bussinessreportanalysisagent.application.preprocessing.chunking import Chunking
from bussinessreportanalysisagent.application.preprocessing.data_loader import PdfLoader


@step()
def load_data_from_dir(dir_path: str, config_data: dict) -> Annotated[list[list[Document]], "loaded_documents"]:
    """Load data from a directory.

    Args:
        dir_path (str): Path to the directory containing the pdf files.

    Returns:
        list[str]: List of file paths.
    """

    logger.info(f"Loading data from directory: {dir_path}")

    try:

        docs = PdfLoader().load_and_parse(
            pdfs_file_path=dir_path,
            keywords_list=config_data['configurations']["content_keywords_list"],
            model_name=config_data['configurations']["llm_model_config"]["groq_model"]["model_id"],
            model_temperature=config_data['configurations']["llm_model_config"]["groq_model"]["temperature"]
        )
        logger.info("Data loaded successfully")
        step_context = get_step_context()
        step_context.add_output_metadata(output_name="loaded_documents", metadata={"dir_path": dir_path})

        return docs
    
    except Exception as e:
        logger.error(f"Error loading data from directory: {e}")
        return []
    

@step()
def parse_and_chunk_data(
    loaded_documents: Annotated[list[list[Document]], "loaded_documents"],
    config_data: dict
) -> Annotated[list[str], "parsed_chunk_documents"]:
    """Parse the loaded documents.

    Args:
        loaded_documents (list[list[Document]]): List of loaded documents.

    Returns:
        list[str]: List of parsed text.
    """
    try:
        logger.info("Parsing data")
        chunking = Chunking(
            model_id=config_data['configurations']["embedding_model_config"]["model_id"],
            chunk_size=config_data['configurations']["embedding_model_config"]["chunk_size"],
            chunk_overlap=config_data['configurations']["embedding_model_config"]["chunk_overlap"],
            max_seq_length=config_data['configurations']["embedding_model_config"]["max_seq_length"]
        )

        chunked_documents = []
        for doc in loaded_documents:
            for page in doc:
                chunked_documents.extend(chunking.chunk_text(page.page_content))

        logger.info("Data parsed successfully")
        step_context = get_step_context()
        step_context.add_output_metadata(output_name="parsed_chunk_documents", metadata={"chunked_documents": chunked_documents})
        return chunked_documents
    except Exception as e:
        logger.error(f"Error parsing data: {e}")
        return []
    