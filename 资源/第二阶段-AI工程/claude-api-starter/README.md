# Claude API Starter

Claude API 项目脚手架，包含多轮对话、流式输出、Tool Use、错误处理和评估框架。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env 文件，填入你的 ANTHROPIC_API_KEY

# 3. 运行示例
python examples/multi_turn.py
python examples/streaming.py
python examples/tool_use.py

# 4. 运行评估
python evaluation/eval_runner.py
```

## 项目结构

```
claude-api-starter/
├── examples/
│   ├── multi_turn.py      # 多轮对话示例
│   ├── streaming.py        # 流式输出示例
│   └── tool_use.py         # Tool Use 示例
├── evaluation/
│   ├── eval_dataset.json   # 评估数据集
│   ├── eval_runner.py      # 评估运行器
│   └── metrics.py          # 评估指标
├── utils/
│   ├── client.py           # Claude API 客户端封装
│   └── retry.py            # 重试机制
├── requirements.txt
└── README.md
```

## 核心概念

### 1. 多轮对话
- 管理对话历史
- 维护上下文状态
- 处理角色交替

### 2. 流式输出
- 实时显示生成内容
- 处理不同内容类型（文本、思考、工具调用）
- 获取完整响应

### 3. Tool Use
- 定义工具 schema
- 自动工具执行循环
- 错误处理

### 4. 评估框架
- 测试用例管理
- 自动化评估
- 结果统计
