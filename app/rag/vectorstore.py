import os
from pathlib import Path
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
)
from langchain_core.documents import Document

from app.config import get_settings


def get_embeddings():
    """임베딩 모델 가져오기 (에러 핸들링 포함)"""
    try:
        # 먼저 HuggingFace 임베딩 시도
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    except Exception:
        try:
            # 백업: 더 간단한 임베딩 모델
            from langchain_huggingface import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception:
            # 최종 백업: 기본 임베딩
            from langchain_community.embeddings import FakeEmbeddings
            return FakeEmbeddings(size=384)


class VectorStoreManager:
    """ChromaDB 벡터 스토어 관리자"""

    def __init__(self):
        self.settings = get_settings()
        self.embeddings = get_embeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        )
        self.vectorstore = None

    def initialize(self) -> Chroma:
        """벡터 스토어 초기화 또는 로드"""
        persist_dir = self.settings.chroma_persist_directory

        if os.path.exists(persist_dir) and os.listdir(persist_dir):
            # 기존 벡터 스토어 로드
            self.vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings,
                collection_name="python_education",
            )
        else:
            # 새 벡터 스토어 생성
            self.vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings,
                collection_name="python_education",
            )

        return self.vectorstore

    def load_documents_from_directory(self, directory: str) -> list[Document]:
        """디렉토리에서 문서 로드"""
        documents = []

        # 텍스트 파일 로드
        txt_loader = DirectoryLoader(
            directory,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            silent_errors=True,
        )
        try:
            documents.extend(txt_loader.load())
        except Exception:
            pass

        # 마크다운 파일 로드
        md_loader = DirectoryLoader(
            directory,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            silent_errors=True,
        )
        try:
            documents.extend(md_loader.load())
        except Exception:
            pass

        # PDF 파일 로드
        pdf_path = Path(directory)
        for pdf_file in pdf_path.glob("**/*.pdf"):
            try:
                loader = PyPDFLoader(str(pdf_file))
                documents.extend(loader.load())
            except Exception:
                pass

        return documents

    def add_documents(self, documents: list[Document]) -> None:
        """문서를 벡터 스토어에 추가"""
        if not documents:
            return

        # 문서 분할
        splits = self.text_splitter.split_documents(documents)

        # 벡터 스토어에 추가
        if self.vectorstore is None:
            self.initialize()

        self.vectorstore.add_documents(splits)

    def add_text(self, text: str, metadata: dict = None) -> None:
        """텍스트를 벡터 스토어에 추가"""
        if metadata is None:
            metadata = {}

        doc = Document(page_content=text, metadata=metadata)
        self.add_documents([doc])

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        """유사도 검색"""
        if self.vectorstore is None:
            self.initialize()

        return self.vectorstore.similarity_search(query, k=k)

    def get_retriever(self, k: int = 4):
        """Retriever 객체 반환"""
        if self.vectorstore is None:
            self.initialize()

        return self.vectorstore.as_retriever(search_kwargs={"k": k})


# 싱글톤 인스턴스
_vectorstore_manager = None


def get_vectorstore_manager() -> VectorStoreManager:
    global _vectorstore_manager
    if _vectorstore_manager is None:
        _vectorstore_manager = VectorStoreManager()
        _vectorstore_manager.initialize()
    return _vectorstore_manager
