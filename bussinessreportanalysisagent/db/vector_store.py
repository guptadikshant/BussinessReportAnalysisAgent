import logging
import os
from typing import List

import loguru
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import Distance, PointStruct, VectorParams
from qdrant_client.models import FieldCondition, Filter
from tqdm import tqdm

from bussinessreportanalysisagent.settings import env_settings
from bussinessreportanalysisagent.db.embeddings import VectorEmbeddings


# Set higher log level for qdrant_client to suppress its logs
loguru.logger.configure(
    handlers=[
        {"sink": lambda _: None, "level": logging.ERROR, "filter": "qdrant_client"}
    ]
)
loguru.logger.configure(
    handlers=[{"sink": lambda _: None, "level": logging.ERROR, "filter": "httpx"}]
)


class QdrantVectorStore:
    """
    Class to handle vector storage and retrieval using Qdrant.
    This class provides methods to create a collection, load data into Qdrant,
    """

    def __init__(
        self, collection_name: str, embedding_model_type: str, embedding_model_id: str
    ) -> None:
        """
        Initialize the QdrantVectorStore with the collection name.
        This method sets up the Qdrant client with the provided URL and API key.
        Args:
            collection_name (str): Name of the collection to be created or used in Qdrant
        """

        self.client: QdrantClient = QdrantClient(
            url=env_settings.QDRANT_HOST_URL, api_key=env_settings.QDRANT_API_KEY
        )
        self.collection_name: str = collection_name
        self.qdrant_url: str = os.getenv("QDRANT_HOST_URL")
        self.qdrant_api_key: str = os.getenv("QDRANT_API_KEY")
        
        # loading embedding model
        if embedding_model_type == "gemini":
            self.doc_store = VectorEmbeddings(model_id=embedding_model_id)
        elif embedding_model_type == "sentence_transformers":
            self.doc_store = VectorEmbeddings(model_id=embedding_model_id)
        else:
            raise ValueError("Unsupported embedding model.")

    def create_collection(self, vector_size: int, distance: str = "Cosine") -> None:
        """
        Create a collection in Qdrant with the specified parameters.

        Args:
            vector_size (int): Size of the vector for the collection
            distance (str): Distance metric for the collection (default: "Cosine")
            logger: Logger object for logging information
        """
        try:
            logger.info(f"Creating collection '{self.collection_name}' in Qdrant.")

            if self.client.collection_exists(collection_name=self.collection_name):
                logger.info(
                    f"Collection '{self.collection_name}' already exists. Returning without creating a new one."
                )
                return

            # Create collection with specified parameters
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                    if distance == "Cosine"
                    else Distance.EUCLID,
                ),
            )

            logger.info(f"Collection '{self.collection_name}' created successfully.")
        except UnexpectedResponse as e:
            logger.error(f"Failed to create collection: {e}")

    def delete_collection(self) -> None:
        """
        Delete the collection from Qdrant.
        """
        try:
            logger.info(f"Deleting collection '{self.collection_name}' from Qdrant.")
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Collection '{self.collection_name}' deleted successfully.")
        except UnexpectedResponse as e:
            logger.error(f"Failed to delete collection: {e}")

    def create_filter_condition(self, relevant_keywords: List[str]) -> Filter:
        """
        Create a filter condition for Qdrant based on relevant keywords.

        Args:
            relevant_keywords (List[str]): List of relevant keywords for filtering

        Returns:
            Filter: Filter condition for Qdrant
        """
        try:
            # one of the skills should be present in the profile
            should_conditions = [
                FieldCondition(key="skills", match=models.MatchValue(value=keyword))
                for keyword in relevant_keywords
                if keyword
            ]
            # search only for the that job title to narrow down the search
            must_conditions = [
                FieldCondition(
                    key="job_title",
                    match=models.MatchValue(value=self.searched_job_title),
                )
            ]

            return Filter(should=should_conditions, must=must_conditions)
        except Exception as e:
            logger.error(f"Failed to create filter condition: {e}")
            return None

    def find_similar_profiles(
        self, query_vector: List[float], relevant_keywords: list, limit: int = 10
    ) -> None:
        """
        Find similar profiles in the Qdrant collection.
        This method is a placeholder and should be implemented based on specific requirements.
        """
        logger.info("Finding similar profiles in Qdrant collection.")
        filter_condition = self.create_filter_condition(relevant_keywords)
        if filter_condition:
            closest_profiles = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter_condition,
            )
            logger.info(f"Found {len(closest_profiles)} similar chunks.")
            return closest_profiles
        else:
            return None

    def bulk_insert_documents(self, documents: List[dict]) -> None:
        """
        Bulk insert documents into Qdrant collection.

        Args:
            documents (List[dict]): List of documents to be inserted

        Returns:
            None
        """
        try:
            logger.info("Inserting documents into Qdrant.")
            doc_points = [
                PointStruct(
                    id=doc.id,
                    vector=self.doc_store.get_embedding(doc.page_content),
                    payload={
                        "profile_details": doc.page_content,
                        "skills": doc.metadata["skills"],
                        "job_title": doc.metadata["job_title"],
                        "profile_id": doc.metadata.get("profile_id", str(doc.id)),
                    },
                )
                for doc in tqdm(documents)
            ]

            # Insert in batches of 100 documents
            batch_size = 100
            for i in range(0, len(doc_points), batch_size):
                batch = doc_points[i : i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                    wait=False,  # Use async operation
                )

            logger.info(f"Inserted {len(documents)} documents into Qdrant.")
        except UnexpectedResponse as e:
            logger.error(f"Failed to insert documents: {e}")

    def load_data_into_qdrant(
        self,
        all_documents: List,
        vector_size: int,
    ) -> None:
        """
        Load data into Qdrant collection.

        Args:
            all_documents (List): List of documents to be inserted
            vector_size (int): Size of the vector for the collection
        """
        try:
            logger.info("Loading data into Qdrant.")

            # Create collection if it doesn't exist
            self.create_collection(vector_size=vector_size)

            # Bulk insert profiles into Qdrant
            self.bulk_insert_documents(all_documents)

        except UnexpectedResponse as e:
            logger.error(f"Failed to load data into Qdrant: {e}")
        except ValueError as v:
            logger.error(f"Value error: {v}")

    def load_data_from_qdrant(
        self,
        job_description: str,
        relevant_keywords: List[str],
        limit: int,
        searched_job_title: str,
        top_k: int = 3,
    ) -> List[dict]:
        """
        Retrieve relevant documents from Qdrant Cloud based on job description and keywords.

        Args:
            job_description (str): The job description to search for
            relevant_keywords (List[str]): List of relevant keywords for filtering
            limit (int): Maximum number of results to return for initial search
            searched_job_title (str): Job title to search for
            top_k (int): Number of top profiles to return

        Returns:
            List[dict]: List of the top_k most relevant profiles
        """
        try:
            logger.info("Loading data from Qdrant.")
            self.searched_job_title = searched_job_title.lower().replace(" ", "_")

            # Get chunks from Qdrant
            retrieved_chunks = self.find_similar_profiles(
                query_vector=self.doc_store.get_embedding(job_description),
                relevant_keywords=relevant_keywords,
                limit=limit,
            )

            if not retrieved_chunks:
                logger.warning("No chunks retrieved from Qdrant.")
                return []

            # Return top profiles with their chunks for downstream processing
            return retrieved_chunks

        except UnexpectedResponse as e:
            logger.error(f"Failed to load data from Qdrant: {e}")
            return []
