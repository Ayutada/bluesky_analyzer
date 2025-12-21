# BlueSky 个人项目 - MBTI 与动物占卜分析器 Implementation Plan

## 🎯 目标描述
构建一个最小可行性产品 (MVP) 网页应用，允许用户输入 BlueSky ID (Handle)，爬取其主页公开内容，利用 LLM 进行人格分析，并返回用户的 MBTI 类型及动物占卜形象。

## 📅 项目时间表 (Estimated Timeline)

| 阶段 | 任务 | 预计耗时 |
| :--- | :--- | :--- |
| **Phase 1: 基础设施** | 搭建 Flask/FastAPI 后端，设置前端基础页面 | 1 Hour |
| **Phase 2: 爬虫实现** | 针对 BlueSky Web 端开发轻量级爬虫 (Requests/BS4) | 2 Hours |
| **Phase 3: AI 分析核心** | 复用现有 Gemini/RAG 逻辑，设计 Prompt 进行人格分析 | 2 Hours |
| **Phase 4: 整合与测试** | 前后端联调，验证分析结果准确性 | 1 Hour |

**总计预计**: ~6 小时开发时间

## 🏗️ 架构设计

### 1. 前端 (Frontend)
- **技术栈**: HTML5, CSS3, Vanilla JavaScript (最小依赖).
- **页面**: 单页应用 (`index.html`)。
    - 输入框: 输入 BlueSky ID (例如 `jay.bsky.social`).
    - 按钮: "开始分析".
    - 结果展示区: 显示 MBTI 类型、动物形象、以及分析报告摘要。

### 2. 后端 (Backend)
- **技术栈**: Python (Flask).
- **接口**:
    - `GET /`: 返回前端页面.
    - `POST /api/analyze`: 接收 `{ handle: "..." }`，返回 JSON 结果.
    - 后端启动文件: `server.py`

### 3. 每个模块的详细计划

#### 🕵️‍♂️ 爬虫模块 (Crawler)
- **目标**: 获取用户的 Bio (简介) 和最近的 Post (帖子).
- **策略**:
    - 直接请求 `https://bsky.app/profile/<handle>`.
    - 使用 `BeautifulSoup` 解析 HTML，提取文本内容.
    - *注意*: 仅依赖公开网页数据，不进行复杂鉴权 (符合最小 demo 原则).

#### 🧠 分析模块 (Analyzer)
- **目标**: 将爬取的文本转化为结构化的人格描述.
- **核心逻辑**:
    - 复用 `rag_bot.py` 中的 `ChatGoogleGenerativeAI` 配置.
    - **Prompt 设计**:
        ```text
        你是一个心理分析专家。请根据以下用户的社交媒体内容：
        [用户内容片段...]

        分析该用户的性格特征，并推断：
        1. MBTI 类型 (例如 INTJ).
        2. 动物占卜形象 (例如 黑豹).
        3. 简短的性格画像描述.
        
        请以 JSON 格式输出.
        ```

## User Review Required
> [!IMPORTANT]
> **BlueSky 爬取限制**: 直接 HTML 爬取可能受限于反爬策略或页面结构变化。作为 MVP，如果 HTML 解析不稳定，备选方案是使用 AT Protocol API (需要更多开发工作)，但本计划优先尝试 HTML 解析以保持轻量。

## Proposed Changes

### Backend
#### [NEW] [server.py](file:///d:/MyDev/mbti_crawler_rag/server.py)
- Flask 应用入口.
- 包含路由逻辑和 API 接口.

#### [NEW] [bsky_crawler.py](file:///d:/MyDev/mbti_crawler_rag/bsky_crawler.py)
- 封装 `get_profile_data(handle)` 函数.
- 处理 HTTP 请求和 HTML 解析.

#### [MODIFY] [rag_bot.py](file:///d:/MyDev/mbti_crawler_rag/rag_bot.py)
- 提取 `llm` 初始化逻辑，使其可被 `server.py` 导入使用，避免代码重复.
- 新增 `analyze_personality(text_data)` 函数.

### Frontend
#### [NEW] [templates/index.html](file:///d:/MyDev/mbti_crawler_rag/templates/index.html)
- 用户界面.

#### [NEW] [static/style.css](file:///d:/MyDev/mbti_crawler_rag/static/style.css)
- 简单的美化样式.

## Verification Plan

### Automated Tests
- **API 测试**: 使用 `curl` 或 Postman 测试 `POST /api/analyze` 接口，确保返回合法的 JSON.
- **爬虫测试**: 编写单元测试脚本，针对已知公开账号 (如官方账号) 验证是否能抓取到文字.

### Manual Verification
1. 启动服务器 `python server.py`.
2. 打开浏览器访问 `http://localhost:5000`.
3. 输入测试账号 (例如自分的常用账号或名人账号).
4. 点击分析，检查页面是否在 10-20 秒内显示合理的结果.
