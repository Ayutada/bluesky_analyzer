import os
from dotenv import load_dotenv

# 1. 加载 .env 中的 API Key
load_dotenv()

# 检查 Key 是否加载成功
if not os.getenv("GOOGLE_API_KEY") or not os.getenv("OPENAI_API_KEY"):
    print("❌ 错误：请检查 .env 文件，确保 GOOGLE_API_KEY 和 OPENAI_API_KEY 已正确填写！")
    exit()

# --- 导入 LangChain 组件 ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 2. 配置模型 (混合架构)

# Chat 模型：使用 Google Gemini 2.0 Flash
# 如果 2.0 预览版不稳定，可以随时改回 "gemini-1.5-flash"
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp", 
    temperature=0
)

# Embedding 模型：使用 OpenAI text-embedding-3-small
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# 3. 加载并处理数据 (核心修改部分)
print("📂 正在扫描 rag_docs 文件夹下的所有 .md 文件 (含子目录)...")

try:
    # DirectoryLoader 配置说明：
    # path: 目标文件夹路径
    # glob: "**/*.md" 表示递归查找所有子文件夹里的 markdown 文件
    # loader_cls: 强制使用 TextLoader (纯文本模式)，避免安装复杂的 unstructured 库
    # loader_kwargs: 必须指定 utf-8，否则读取中文/日文文件会报错
    loader = DirectoryLoader(
        path="./rag_docs", 
        glob="**/*.md", 
        loader_cls=TextLoader,
        loader_kwargs={'encoding': 'utf-8'}
    )
    
    docs = loader.load()
    print(f"✅ 成功加载 {len(docs)} 个文件。")

    # 文本切分 (Chunking)
    # chunk_size=1000: 每个片段约 1000 字符
    # chunk_overlap=200: 片段之间重叠 200 字符，保证上下文连贯
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    print(f"✂️  切分完成，共生成 {len(splits)} 个文档片段。")
    print("🚀 正在建立向量数据库 (调用 OpenAI Embedding API)...")

    # 4. 建立向量数据库
    vectorstore = FAISS.from_documents(splits, embeddings)
    retriever = vectorstore.as_retriever()
    print("💾 向量数据库建立完毕！")

except Exception as e:
    print(f"❌ 读取文件出错: {e}")
    print("请检查：1. rag_docs 文件夹是否存在 2. 文件是否为有效的 markdown 格式")
    exit()

# 5. 定义 RAG 的 Prompt 模板
template = """
你是一个精通 MBTI 人格理论的专家助手。
请基于下面的【背景信息】回答用户的【问题】。
如果背景信息里没有答案，请诚实地说不知道，不要编造。

【背景信息】：
{context}

【用户问题】：
{question}
"""
prompt = ChatPromptTemplate.from_template(template)

# 6. 构建 RAG 链
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# --- 交互式问答循环 ---
print("\n=== 🤖 MBTI 智能助手已就绪 (输入 'exit' 退出) ===")

while True:
    user_input = input("\n请提问 (例如: ENFJ的优缺点是什么?): ")
    if user_input.lower() in ["exit", "quit", "q"]:
        print("再见！👋")
        break
    
    if not user_input.strip():
        continue

    print("Thinking...", end="", flush=True)
    try:
        response = rag_chain.invoke(user_input)
        # 清除 "Thinking..." 并打印回答
        print(f"\r{' ' * 20}\r", end="") 
        print(f"🗣️  回答: {response}")
    except Exception as e:
        print(f"\n❌ 调用出错: {e}")