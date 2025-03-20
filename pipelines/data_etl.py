from zenml import pipeline
from loguru import logger
from steps.etl import load_data_from_dir


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
    load_data_from_dir(dir_path=dir_path, config_file_path=config_file_path)
    logger.info("Data ETL pipeline completed successfully")
