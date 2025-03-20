import os
from langchain.document_loaders.pdf import PyMuPDFLoader
file_path = "BusinessReports"


for file in os.listdir(file_path):
    if file.endswith(".pdf"):
        # data = PyMuPDFLoader(file_path=os.path.join(file_path, file)).load()
        data = PyMuPDFLoader(file_path=os.path.abspath(file)).load()
        print(data[0].page_content)
        break
    else:
        print("Not a pdf file")