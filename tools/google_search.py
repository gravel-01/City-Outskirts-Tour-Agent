import json
import os
import requests
from dotenv import load_dotenv


def google_search(search_query: str) -> str:
    """执行谷歌搜索并返回格式化的结果内容"""
    url = "https://google.serper.dev/search"
    load_dotenv()

    # 1. 准备请求数据
    payload = json.dumps({"q": search_query})
    api_key = os.getenv("SERPER_API_KEY")
    print(api_key)
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    try:
        # 2. 发送 POST 请求
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # 检查请求是否成功

        # 3. 解析结果
        result = response.json()

        # 4. 提取关键信息并格式化
        # serper 通常返回有机搜索结果（organic）、知识图谱（knowledgeGraph）等
        search_results = []

        # 提取知识图谱的描述（如果有）
        if "knowledgeGraph" in result:
            kg = result["knowledgeGraph"]
            search_results.append(f"摘要: {kg.get('description', '无描述')}")

        # 提取前几条搜索结果的标题和摘要
        for item in result.get("organic", [])[:3]:  # 取前3条结果
            search_results.append(f"标题: {item['title']}\n内容: {item['snippet']}")

        if not search_results:
            return "没有找到相关的搜索结果。"

        return "\n\n".join(search_results)

    except Exception as e:
        return f"错误: 搜索执行失败 - {str(e)}"


GOOGLE_SEARCH = {
    "name_for_human": "谷歌搜索",
    "name_for_model": "google_search",
    "description_for_model": "谷歌搜索是一个通用搜索引擎，可用于访问互联网、查询百科知识、了解时事新闻等。",
    "parameters": [
        {
            "name": "search_query",
            "description": "搜索关键词或短语",
            "required": True,
            "schema": {"type": "string"},
        }
    ],
}
