import os
from tqdm import tqdm
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from loguru import logger

from bussinessreportanalysisagent.services.content_keyword_generation import ContentKeyword
from bussinessreportanalysisagent.validations.file_name_validation import AnnualReportFile

class PdfLoader:

    @staticmethod
    def load_and_parse(pdfs_file_path, keywords_list: list[str], model_name: str, model_temperature: int) -> list[list[Document]]:

        logger.info("Pdf parsing started....................")
        all_documents = []
        try:
            logger.info(f"parsing: {pdfs_file_path}")
            for pdf_name in os.listdir(pdfs_file_path):
                # Check if the file is a PDF
                report = AnnualReportFile(filename=pdf_name)
                loaded_docs = PyMuPDFLoader(file_path=os.path.join(pdfs_file_path, pdf_name)).load()
                # logger.debug(f"Meta data keyword extraction started:{docs.company_name}")
                newDoc = []
                i = 0
                for doc in tqdm(loaded_docs, desc=f"Processing {pdf_name}", unit="page"):
                    all_keyword = ContentKeyword.get_content_keyword(
                        keywords_list=keywords_list,
                        content=doc.page_content,
                        model_name=model_name,
                        model_temperature=model_temperature
                    )
                    logger.debug("Keyword:", all_keyword)
                    meta_data = doc.metadata
                    if len(all_keyword):
                        i += 1
                        for newKeyword in all_keyword:
                            meta_data[newKeyword] = newKeyword

                    meta_data['Company_Name'], meta_data['Document_Type'], meta_data[
                        'Year'] = report.company_name, report.document_type, report.year
                    newDoc.append(Document(page_content=doc.page_content, meta_data=meta_data))
                all_documents.append(newDoc)

            return all_documents
        
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
        
        except ValueError as e:
            logger.error(f"Value error: {e}")

        except Exception as e:
            logger.exception(f"Some thing went wrong in pdf loader: {e}")
