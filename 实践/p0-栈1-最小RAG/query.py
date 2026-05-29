"""查询 RAG：加载 Chroma 索引 → 检索 → 调兼容端点 LLM 生成 → 打印答案与引用。

用法：python query.py "你的问题"
"""
import os
import sys
import chromadb
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.vector_stores.chroma import ChromaVectorStore

HERE = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(HERE, 'chroma_db')
COLLECTION = 'p0_rag'

load_dotenv(os.path.join(HERE, '.env'))


def build_llm():
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE')
    model = os.getenv('LLM_MODEL')
    if not (api_key and api_base and model):
        sys.exit('请先在 .env 配置 OPENAI_API_KEY / OPENAI_API_BASE / LLM_MODEL')
    # is_chat_model=True 走 /chat/completions；context_window 给个保守值
    return OpenAILike(
        model=model, api_key=api_key, api_base=api_base,
        is_chat_model=True, context_window=8192, timeout=60,
    )


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else '这些文档讲了什么？'

    Settings.embed_model = HuggingFaceEmbedding(model_name='BAAI/bge-small-zh-v1.5')
    Settings.llm = build_llm()

    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_or_create_collection(COLLECTION)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    index = VectorStoreIndex.from_vector_store(vector_store)

    engine = index.as_query_engine(similarity_top_k=3)
    resp = engine.query(question)

    print('\n=== 问题 ===')
    print(question)
    print('\n=== 回答 ===')
    print(resp)
    print('\n=== 引用来源 ===')
    for i, node in enumerate(resp.source_nodes, 1):
        fname = node.metadata.get('file_name', '?')
        print(f'[{i}] 相关度 {node.score:.3f} | 来源 {fname}')
        print(f'    {node.text[:80].strip()}...')


if __name__ == '__main__':
    main()
