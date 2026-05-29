"""建立 RAG 索引：读 docs/ → 切块 → 本地嵌入 → 写入 Chroma。

首次运行或文档更新后执行。嵌入用本地 fastembed，不调远程 API。
"""
import os
import chromadb
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(HERE, 'docs')
DB_DIR = os.path.join(HERE, 'chroma_db')
COLLECTION = 'p0_rag'


def main():
    # 本地嵌入模型：中文小模型，首次会自动下载到缓存
    Settings.embed_model = HuggingFaceEmbedding(model_name='BAAI/bge-small-zh-v1.5')
    # 切块：中文按 512 字符、重叠 50，便于检索定位
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    docs = SimpleDirectoryReader(DOCS_DIR, recursive=True).load_data()
    print(f'读到 {len(docs)} 个文档片段')

    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_or_create_collection(COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        docs, storage_context=storage_context, show_progress=True
    )
    print(f'索引完成，向量库已持久化到 {DB_DIR}')
    return index


if __name__ == '__main__':
    main()
