"""FAQ 知识库检索模块

使用 sentence-transformers 本地模型进行 Embedding，
FAISS 向量存储实现语义检索，无需 OpenAI API。
"""

import json
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


# 使用轻量级中文模型
EMBEDDING_MODEL = "shibing624/text2vec-base-chinese"


class FAQRetriever:
    """FAQ 知识库检索器

    使用 FAISS 向量存储 + 本地 Embeddings 实现 FAQ 语义检索
    """

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self.vectorstore: FAISS | None = None
        self._load_or_create_index()

    def _load_or_create_index(self):
        """加载或创建 FAQ 向量索引"""
        index_path = Path(__file__).parent / "faiss_index"
        if index_path.exists():
            self.vectorstore = FAISS.load_local(
                str(index_path), self.embeddings, allow_dangerous_deserialization=True
            )
        else:
            self._build_index()

    def _build_index(self):
        """从 FAQ 数据构建向量索引"""
        faq_path = Path(__file__).parent / "faq_data.json"
        with open(faq_path, "r", encoding="utf-8") as f:
            faq_data = json.load(f)

        documents = []
        for item in faq_data:
            search_text = f"{item['question']} {' '.join(item.get('keywords', []))}"
            doc = Document(
                page_content=search_text,
                metadata={
                    "id": item["id"],
                    "question": item["question"],
                    "answer": item["answer"],
                    "category": item["category"],
                },
            )
            documents.append(doc)

        self.vectorstore = FAISS.from_documents(documents, self.embeddings)

        # 保存索引
        index_path = Path(__file__).parent / "faiss_index"
        self.vectorstore.save_local(str(index_path))

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """检索相关 FAQ

        Args:
            query: 用户查询
            top_k: 返回结果数

        Returns:
            FAQ 列表，每项包含 question、answer、category、score
        """
        if not self.vectorstore:
            return []

        results = self.vectorstore.similarity_search_with_score(query, k=top_k)

        faq_results = []
        for doc, score in results:
            faq_results.append({
                "question": doc.metadata["question"],
                "answer": doc.metadata["answer"],
                "category": doc.metadata["category"],
                "score": float(score),
            })

        return faq_results

    def rebuild_index(self):
        """重建索引（FAQ 数据更新后调用）"""
        self._build_index()


# 全局 FAQ 检索器实例
_faq_retriever: FAQRetriever | None = None


def get_faq_retriever() -> FAQRetriever:
    """获取 FAQ 检索器单例"""
    global _faq_retriever
    if _faq_retriever is None:
        _faq_retriever = FAQRetriever()
    return _faq_retriever
