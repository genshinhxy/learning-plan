# VLM 副项目与评测专精路线图

> **项目名**：面向 VLM 的结构化负样本生成与细粒度图文对齐评测
> **定位**：复用你的 Structure-CLIP 积累，升级到现代 VLM。多模态岗位敲门砖 + 第二篇投稿。
> **时长**：第 12-18 月（与主项目 P2 并行，30% 精力）

---

## 0. 为什么是这个项目

- 你已有 Structure-CLIP、场景图、三元组、难负样本的真实背景，**起点远高于从零开始**。
- "结构化负样本 + 细粒度对齐评测"和主线共享底座（结构化语义、评测数据构造），不是另起炉灶。
- 现代 VLM（LLaVA/Qwen-VL/InternVL）在细粒度组合理解上仍有明显短板，有研究空间。

---

## 第 1 步：复现与对齐认知（第 12-13 月）

### 做什么
1. 复现你自己的 Structure-CLIP（arXiv:2305.06152），重新跑通，确认环境和指标。
2. 读懂细粒度评测这条线，理解"组合性理解"问题是什么：
   - ARO/NegCLIP：属性、关系、顺序的对抗测试
   - SugarCrepe：修正了前人评测的语言偏置（**必读，是当前标准**）
   - Winoground：极难的组合性 benchmark
3. **关键警示——先读 "The Hard Positive Truth"（arXiv:2409.17958）**：
   - 它指出很多"难负样本提升"其实是评测偏置造成的假象。
   - 做副项目前必须读懂，否则容易做出看似有效、实则有偏的方法。

### 必读链（按顺序）
Structure-CLIP(2305.06152) → ARO/NegCLIP(2210.01936) → SugarCrepe(2306.14610) → Hard Positive Truth(2409.17958)

### 产出
Structure-CLIP 复现成功 + 一份"细粒度对齐评测现状与陷阱"笔记。

---

## 第 2 步：迁移到现代 VLM（第 14-15 月）

### 做什么
1. 选定目标 VLM：建议 **Qwen2.5-VL** 或 **InternVL3**（开源、强、社区活跃），LLaVA-OneVision 作对照。
2. 测现代 VLM 在 SugarCrepe/ARO 上的细粒度表现，找出它们的弱项（关系？属性绑定？计数？）。
3. 把场景图/结构化负样本的思路从 CLIP 时代迁移到 VLM：
   - CLIP 是双塔对比；现代 VLM 是生成式，负样本如何利用是新问题。
   - 探索：结构化负样本用于 VLM 的偏好对齐（DPO）或评测探针。

### 必读论文
- arXiv:2502.13923 Qwen2.5-VL / arXiv:2504.10479 InternVL3
- arXiv:2408.03326 LLaVA-OneVision
- arXiv:2306.13549 MLLM Survey（建立现代 VLM 全景）
- arXiv:2305.19595 DAC（密集对齐的负样本方法参考）

### 产出
现代 VLM 在细粒度对齐上的弱项分析报告 + 迁移方案设计。

---

## 第 3 步：构造评测基准 / 方法（第 16-17 月）

### 两条路线，择一（或结合）

**路线 A：评测基准（更稳，容易成文）**
- 基于场景图自动构造结构化的细粒度评测集（属性绑定、关系方向、组合）。
- 用 SugarCrepe 的去偏方法论确保评测不被语言模型偏置污染。
- 评测主流 VLM，给出排行榜 + 失败模式分析。

**路线 B：方法改进（更亮，风险高）**
- 用结构化负/正样本对 VLM 做偏好对齐（参考 RLHF-V / POVID 的 DPO 范式）。
- 证明能提升细粒度组合理解，且不引入偏置（用 Hard Positive Truth 的检验标准自查）。

### 必读论文
- arXiv:2406.11171 SugarCrepe++（评测构造进阶）
- arXiv:2312.00849 RLHF-V / arXiv:2402.11411 POVID（VLM 偏好对齐）
- arXiv:2305.10355 POPE / arXiv:2310.14566 HallusionBench（幻觉评测，可作延伸维度）
- arXiv:2408.15769 MLLM 评测综述

### 产出
一个细粒度图文对齐评测基准，或一个结构化负样本对齐方法，达投稿标准。

---

## 第 4 步：投稿与打包（第 18 月）

### 论文侧
- 评测类工作适合投：CVPR/ICCV/ACL 的 benchmark track，或相关 workshop。
- 开源评测集 + 评测代码，提升影响力。

### 简历侧
- 包装为"代表作 2"：多模态细粒度对齐 + 评测能力。
- 强调与主项目共享的"结构化语义建模 + 评测数据构造"底座，形成完整人设。

### 产出
- 第二篇投稿
- 多模态岗位的代表作

---

## 里程碑检查表

- [ ] 第 13 月：Structure-CLIP 复现 + 评测陷阱笔记（含 Hard Positive Truth）
- [ ] 第 15 月：现代 VLM 弱项分析 + 迁移方案
- [ ] 第 17 月：评测基准 / 对齐方法完成
- [ ] 第 18 月：投稿 + 简历打包

---

## 关键提醒

1. **先读 Hard Positive Truth 再动手**——这是整个副项目最重要的前置认知，避免方向性错误。
2. **评测优于方法**——若时间紧，优先做扎实的评测基准（成文稳、复用你的数据构造能力），方法改进作为加分项。
3. **与主项目错峰**——副项目在主项目消融期（P2）并行，避免两边同时冲刺。

---

## 资源速查

| 类型 | 资源 |
|------|------|
| 你的背景工作 | Structure-CLIP https://github.com/zjukg/Structure-CLIP |
| 评测必读 | SugarCrepe https://github.com/RAIVNLab/sugar-crepe |
| 评测对抗集 | ARO/NegCLIP https://github.com/mertyg/vision-language-models-are-bows |
| 现代 VLM | Qwen2.5-VL / InternVL / LLaVA-NeXT |
| CLIP 训练 | open_clip https://github.com/mlfoundations/open_clip |
| VLM 偏好对齐 | RLHF-V / POVID |
| 幻觉评测 | POPE / HallusionBench |
| MLLM 论文索引 | https://github.com/BradyFU/Awesome-Multimodal-Large-Language-Models |
| 论文 PDF/clone 命令 | 见 `资源/00-资源获取清单/资源获取清单.md` |