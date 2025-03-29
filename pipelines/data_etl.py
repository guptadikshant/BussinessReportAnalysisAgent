from loguru import logger
from zenml import pipeline

from steps.etl import load_data_from_dir, parse_and_chunk_data
from steps.utils import load_config_data


@pipeline(enable_cache=False)
def data_etl_pipeline(
    dir_path: str,
    config_file_path: str,
) -> None:
    """Pipeline to load data from a directory and parse it.

    Args:
        dir_path (str): Path to the directory containing the pdf files.
        config_file_path (str): Path to the configuration file.
    """
    logger.info("Starting data ETL pipeline")
    # Load configuration data
    config_data = load_config_data(config_file_path)

    docs = load_data_from_dir(dir_path=dir_path, config_data=config_data)
    parse_and_chunk_data(loaded_documents=docs, config_data=config_data)
    logger.info("Data ETL pipeline completed successfully")
