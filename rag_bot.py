import os
from dotenv import load_dotenv

# 1. 加载 .env 中的 API Key
load_dotenv(os.path.join(os.path.dirname(__file__), 'env', '.env'))

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

# 3. 加载并处理数据 - 针对三个语言版本
def load_and_build_vectorstore(language, folder_path):
    """
    为指定语言加载文档并建立向量数据库
    """
    print(f"\n📂 正在扫描 {folder_path} 文件夹下的所有 .md 文件...")
    
    try:
        loader = DirectoryLoader(
            path=folder_path, 
            glob="*.md", 
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        
        docs = loader.load()
        print(f"✅ {language} 版本：成功加载 {len(docs)} 个文件。")

        # 文本切分 (Chunking)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        print(f"✂️  切分完成，共生成 {len(splits)} 个文档片段。")
        print(f"🚀 正在为 {language} 版本建立向量数据库...")

        # 建立向量数据库
        vectorstore = FAISS.from_documents(splits, embeddings)
        vectorstore.save_local(f"./rag_vectorstore_{language}")
        print(f"💾 {language} 版本的向量数据库已保存！")
        
        return vectorstore
        
    except Exception as e:
        print(f"❌ {language} 版本读取文件出错: {e}")
        return None

# 加载三个语言版本的数据
languages = {
    "cn": "./rag_docs/cn",
    "en": "./rag_docs/en",
    "jp": "./rag_docs/jp"
}

vectorstores = {}
for lang_code, folder_path in languages.items():
    if os.path.exists(folder_path):
        vectorstores[lang_code] = load_and_build_vectorstore(lang_code, folder_path)
    else:
        print(f"⚠️  警告：{folder_path} 文件夹不存在，跳过 {lang_code} 版本")

if not vectorstores:
    print("❌ 错误：没有成功加载任何语言版本的数据!")
    exit()

print(f"\n✅ 成功加载 {len(vectorstores)} 个语言版本的数据库")

# 5. 定义 RAG 的 Prompt 模板
templates = {
    "cn": """
你是一个精通 MBTI 人格理论的专家助手。
请基于下面的【背景信息】回答用户的【问题】。
如果背景信息里没有答案，请诚实地说不知道，不要编造。

【背景信息】：
{context}

【用户问题】：
{question}
""",
    "en": """
You are an expert assistant proficient in MBTI personality theory.
Please answer the user's【question】based on the following【background information】.
If the background information does not contain the answer, please honestly say you don't know, don't make it up.

【Background Information】:
{context}

【User Question】:
{question}
""",
    "jp": """
あなたはMBTI人格理論に精通した専門家アシスタントです。
以下の【背景情報】に基づいて、ユーザーの【質問】に答えてください。
背景情報に答えがない場合は、正直に知らないと言ってください。作り話をしないでください。

【背景情報】：
{context}

【ユーザーの質問】：
{question}
"""
}

prompts = {lang: ChatPromptTemplate.from_template(template) for lang, template in templates.items()}

# 6. 构建三个语言版本的 RAG 链
rag_chains = {}
for lang_code, vectorstore in vectorstores.items():
    retriever = vectorstore.as_retriever()
    rag_chains[lang_code] = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompts[lang_code]
        | llm
        | StrOutputParser()
    )
    print(f"✅ {lang_code.upper()} RAG 链建立完成")

# --- 交互式问答循环 ---
if __name__ == "__main__":
    print("\n=== 🤖 MBTI 智能助手已就绪 ===")
    print("支持语言: CN (中文), EN (英文), JP (日文)")
    print("输入 'exit' 退出\n")

    current_language = "cn"  # 默认中文

    while True:
        lang_hint = f"[{current_language.upper()}]"
        user_input = input(f"\n{lang_hint} 请提问 (或输入 'lang' 切换语言): ")
        
        # 处理语言切换
        if user_input.lower() == "lang":
            print("\n选择语言: CN (中文) | EN (英文) | JP (日文)")
            lang_choice = input("输入语言代码: ").lower()
            if lang_choice in rag_chains:
                current_language = lang_choice
                print(f"✅ 已切换至 {lang_choice.upper()} 版本")
            else:
                print(f"❌ 不支持的语言代码: {lang_choice}")
            continue
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("再见！👋")
            break
        
        if not user_input.strip():
            continue

        print("Thinking...", end="", flush=True)
        try:
            response = rag_chains[current_language].invoke(user_input)
            # 清除 "Thinking..." 并打印回答
            print(f"\r{' ' * 20}\r", end="") 
            print(f"🗣️  回答: {response}")
        except Exception as e:
            print(f"\n❌ 调用出错: {e}")

# --- 新增：用于 BlueSky 分析的函数 ---
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class PersonalityAnalysis(BaseModel):
    mbti: str = Field(description="推断的 MBTI 类型，例如 INTJ")
    animal: str = Field(description="推断的动物占卜形象，例如 黑豹")
    description: str = Field(description="简短的性格画像描述，约 50-100 字")

def analyze_personality(text_content):
    """
    根据用户输入的文本内容，分析 MBTI 和动物形象。
    返回 JSON 格式数据。
    """
    parser = JsonOutputParser(pydantic_object=PersonalityAnalysis)
    
    prompt = ChatPromptTemplate.from_template(
        """
        你是一个精通 MBTI 人格理论和动物占卜的心理分析专家。
        请仔细阅读以下用户的社交媒体内容（包括简介和帖子），深入分析其言行风格、价值观和思维模式。

        【用户内容】：
        {text}

        请推断：
        1. 该用户的 MBTI 类型 (16型人格)。
        2. 该用户在“动物占卜”中对应的动物形象 (Animal Fortune)。
        3. 生成一段简短的性格画像。

        请务必按照 JSON 格式输出，不要包含 Markdown 格式标记 (```json ... ```)。
        
        {format_instructions}
        """
    )

    chain = prompt | llm | parser

    try:
        print("🧠 正在进行 AI 人格分析...")
        result = chain.invoke({
            "text": text_content,
            "format_instructions": parser.get_format_instructions()
        })
        return result
    except Exception as e:
        print(f"❌ AI 分析失败: {e}")
        return {
            "mbti": "Unknown",
            "animal": "Unknown", 
            "description": "分析过程中出现错误，请稍后再试。"
        }