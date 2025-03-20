from services.loader import PdfLoader
from langchain_core.documents import Document
from services.recursivesplitter import RecursiveSplitter
from services.chromdb import ChromaDb
from services.businessReportRetrieval import BusinessReportRetrieval
from services.questionKeyword import QuestionKeywords


class BusinessAnalysisController:

    def __init__(self):
        self.pdfLoader = PdfLoader()
        self.recursiveSplitter = RecursiveSplitter()
        self.chromaDb = ChromaDb()
        self.businessReportRetrieval = BusinessReportRetrieval()
        self.questionKeyword = QuestionKeywords()

    def qnaResponse(self, user_question: str, companyName: str):
        print("Retrieve Summary started")
        response = self.businessReportRetrieval.qnaResponse(user_question, companyName)
        print("Retrieve Summary Completed")
        return response

    def summaryResponse(self, user_question: str, companyName: str, keyword: str):
        print("Retrieve Summary started")
        response = self.businessReportRetrieval.summaryResponse(user_question, companyName, keyword)
        print("Retrieve Summary Completed")
        return response

    def trendAnalysis(self, keyword: list[str], trendTemplate: str) -> str:
        try:
            print("Trends retrieval started:")
            responseTrends: str = self.businessReportRetrieval.trendAnalysis(keyword, trendTemplate)
            print("Trends retrieval completed:")
            return responseTrends
        except Exception as e:
            print("Something went wrong in trends retrieval:", e)

    def telecomTrends(self, keyword: list[str]) -> str:
        try:
            print("Trends retrieval started:")
            responseTrends: str = self.businessReportRetrieval.retrieveTelecomTrends(keyword)
            print("Trends retrieval completed:")
            return responseTrends
        except Exception as e:
            print("Something went wrong in trends retrieval:", e)

    def loader(self, pdf: object) -> list[list[Document]]:
        return self.pdfLoader.load_and_parse(pdf)

    def chunking(self, allDocument: list[list[Document]]) -> list[Document]:
        return self.recursiveSplitter.split(allDocument)

    def saveEmbedding(self, allChunk: list[Document], collectionName: str) -> str:
        return self.chromaDb.createEmbeddingAndStore(allChunk, collectionName)
