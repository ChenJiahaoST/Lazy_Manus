import os
import requests

from lazyllm.tools import fc_register
from lazyllm import LOG
from dotenv import load_dotenv
load_dotenv()


@fc_register("tool")
def web_search(query: str) -> str:
    """
    搜索与query相关的网页，搜索结果包含每个搜索结果的标题、简介和链接。

    Args:
        query (str): The search query string.
    """
    LOG.info(f"[tool - Bocha Search] Searching the web for query '{query}'...")
    url = "https://api.bochaai.com/v1/web-search"
    headers = {
        "Authorization": f"Bearer {os.getenv('BOCHA_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "summary": True,
        "count": 3
    }
    res_str = ""
    response = requests.post(url, headers=headers, json=payload)
    try:
        if response.status_code == 200:
            data = response.json().get('data', {})
            for web_page in data.get('webPages', {}).get('value', []):
                link = web_page.get("url")
                title = web_page.get("name")
                snippet = web_page.get("summary")
                res_str += f"Title: {title}\nSnippet: {snippet[:30]}...\nURL: {link}\n\n"
            return res_str
    except Exception as e:
        return "Error: search failed"