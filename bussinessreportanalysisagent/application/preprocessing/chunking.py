from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)


class Chunking:
    _instance = None

    def __new__(
        cls,
        model_id: str,
        max_seq_length: int,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        if cls._instance is None:
            cls._instance = super(Chunking, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(
        self,
        model_id: str,
        max_seq_length: int,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize the Chunking class with a model ID and optional chunk size and overlap.
        This method sets up the text splitter and token text splitter for chunking text.
        Args:
            model_id (str): The model ID to be used for the token text splitter.
            chunk_size (int, optional): The size of each chunk. Defaults to 1000.
            chunk_overlap (int, optional): The overlap between chunks. Defaults to 200.
        """
        # Only initialize once
        if not hasattr(self, "initialized") or not self.initialized:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
            )
            self.token_text_splitter = SentenceTransformersTokenTextSplitter(
                model_name=model_id,
                chunk_overlap=chunk_overlap,
                tokens_per_chunk=max_seq_length,
            )
            self.initialized = True

    def chunk_text(self, text: str) -> list[str]:
        """
        Chunk the text into smaller pieces.
        This method first splits the text into sections based on a character limit, and
        then further splits each section into smaller chunks based on token count.

        Args:
            text (str): The text to be chunked.This text is expected to be a long string,
                        such as a document or report.

        Returns:
            list[str]: A list of text chunks, where each chunk is a string.
        """
        text_split_by_character = self.text_splitter.split_text(text)

        chunks_by_token = []

        for section in text_split_by_character:
            chunks_by_token.extend(self.token_text_splitter.split_text(section))

        return chunks_by_token
