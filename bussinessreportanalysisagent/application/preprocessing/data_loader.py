import os
import time
from tqdm import tqdm
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from loguru import logger

from bussinessreportanalysisagent.services.content_keyword_generation import ContentKeyword

class PdfLoader:

    @staticmethod
    def load_and_parse(pdfs_file_path, keywords_list: list[str], model_name: str, model_temperature: int) -> list[list[Document]]:

        logger.info("Pdf parsing started....................")
        all_documents = []
        try:
            logger.info(f"parsing: {pdfs_file_path}")
            for pdf_name in os.listdir(pdfs_file_path):
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
                    metaData = doc.metadata
                    if len(all_keyword):
                        i += 1
                        for newKeyword in all_keyword:
                            metaData[newKeyword] = newKeyword

                    # metaData['Company_Name'], metaData['File_Name'], metaData['Document_Type'], metaData[
                    #     'Year'] = docs.company_name, docs.filename, docs.document_type, docs.year
                    newDoc.append(Document(page_content=doc.page_content, metadata=metaData))
                    time.sleep(2)
                all_documents.append(newDoc)

            return all_documents

        except Exception as e:
            logger.exception(f"Some thing went wrong in pdf loader: {e}")
