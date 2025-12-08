import os
import requests
import re
import time  # <--- 新增：用于让爬虫休息，防止被封
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# --- 配置区域 ---
OUTPUT_FOLDER = "rag_docs\jp"

# 定义 16 种人格的代码列表
MBTI_TYPES = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

def fetch_and_save(url, folder):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"🔄 正在爬取: {url} ...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, "html.parser")
        
        # 处理文件名（去除非法字符）
        if soup.title and soup.title.string:
            raw_title = soup.title.string.strip()
            page_title = re.sub(r'[\\/*?:"<>|]', "_", raw_title)
        else:
            page_title = "未知标题_" + str(int(time.time()))
        
        # 提取内容并转为 Markdown
        content_html = str(soup.body) 
        markdown_content = md(content_html, heading_style="ATX")

        # 检查文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        file_path = os.path.join(folder, f"{page_title}.md")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Source: {url}\n\n")
            f.write(markdown_content)
            
        print(f"✅ 成功保存: {file_path}")

    except Exception as e:
        print(f"❌ 此页面爬取失败: {url}")
        print(f"   错误信息: {e}")

if __name__ == "__main__":
    print(f"🚀 开始批量爬取 16 种人格，共 {len(MBTI_TYPES)} 个任务...\n")
    
    for mbti_type in MBTI_TYPES:
        # 构造 URL：通常是 /ch/代码-人格，注意代码通常小写
        # 例如: https://www.16personalities.com/ch/intj-人格
        target_url = f"https://www.16personalities.com/ja/{mbti_type.lower()}型の性格"
        
        fetch_and_save(target_url, OUTPUT_FOLDER)
        
        # 这里的等待非常关键，做个有礼貌的爬虫
        print("⏳ 休息 2 秒，准备下一个...") 
        time.sleep(2)
        
    print("\n🎉 全部任务完成！")