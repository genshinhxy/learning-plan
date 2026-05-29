# P0 栈1：最小 RAG

LlamaIndex + 本地 fastembed 嵌入 + 本地 Chroma 向量库 + 兼容端点 LLM。
验证"文档 → 切块 → 向量化 → 检索 → 生成 + 引用"全链路。

## 设计要点
- **嵌入走本地**（HuggingFace，BAAI/bge-small-zh-v1.5），不依赖代理是否提供 embedding 接口，离线、免费。
- **生成走兼容端点**（OpenAI 协议），用 OpenAILike 适配国内代理。
- **向量库本地持久化**（Chroma，存 ./chroma_db），重跑不必重新嵌入。

## 使用
```bash
# 1. 配置（复制后填入真实信息，.env 不进 git）
cp .env.example .env

# 2. 放文档：把 .txt / .md / .pdf 丢进 docs/
#    （已自带一个示例 docs/sample.md，可直接试）

# 3. 建索引（首次或文档更新后跑）
"D:/Anaconda/python.exe" build_index.py

# 4. 问答
"D:/Anaconda/python.exe" query.py "你的问题"
```

## 文件
- `build_index.py` — 读 docs/、切块、本地嵌入、写入 Chroma
- `query.py` — 加载索引、检索、调 LLM 生成、打印答案 + 引用来源
- `docs/` — 你的知识库文档
- `chroma_db/` — 向量库持久化目录（不进 git）
