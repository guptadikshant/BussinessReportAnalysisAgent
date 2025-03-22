import argparse
import sys
from loguru import logger
from dotenv import load_dotenv, find_dotenv
from pipelines.data_etl import data_etl_pipeline


# Load environment variables from .env file
load_dotenv(find_dotenv())

# Set up logging configuration
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run ETL pipeline")
    parser.add_argument(
        "--dir_path",
        type=str,
        help="Path to the directory containing the pdf files",
        required=True,
    )
    parser.add_argument(
        "--config_file_path",
        type=str,
        default=".\steps\config.yml",
        help="Path to the configuration file",
        required=True,
    )

    args = parser.parse_args()

    dir_path = args.dir_path
    config_file_path = args.config_file_path

    logger.info(f"Directory path: {dir_path}")
    logger.info(f"Configuration file path: {config_file_path}")
    
    # Run the ETL pipeline
    data_etl_pipeline(
        dir_path=dir_path,
        config_file_path=config_file_path,
    )
    logger.info("ETL pipeline completed successfully")


if __name__ == "__main__":
    main()