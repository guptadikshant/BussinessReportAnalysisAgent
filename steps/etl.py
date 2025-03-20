from zenml import step, get_step_context
from loguru import logger
from typing_extensions import Annotated
from langchain_core.documents import Document
from bussinessreportanalysisagent.application.preprocessing.data_loader import PdfLoader
from steps.utils import load_config_data

@step()
def load_data_from_dir(dir_path: str, config_file_path: str) -> Annotated[list[list[Document]], "loaded_documents"]:
    """Load data from a directory.

    Args:
        dir_path (str): Path to the directory containing the pdf files.

    Returns:
        list[str]: List of file paths.
    """

    logger.info(f"Loading data from directory: {dir_path}")

    try:

        config_data = load_config_data(config_file_path)

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
