import os
import requests
from dotenv import load_dotenv

load_dotenv()

MY_KEY = os.getenv("GAODEDITY_API_KEY")


def get_districts(keywords="成都市", subdistrict=1):
    """
    通用行政区域查询
    keywords: 城市名/adcode
    subdistrict: 期望返回的下级层级
    """
    params = {
        "key": MY_KEY,
        "keywords": keywords,
        "subdistrict": subdistrict,
        "extensions": "base",
    }
    try:
        res = requests.get(
            "https://restapi.amap.com/v3/config/district", params=params
        ).json()
        if res["status"] == "1" and res["districts"]:
            # 返回下级行政区的名称列表
            return [d["name"] for d in res["districts"][0].get("districts", [])]
        return []
    except Exception as e:
        print(f"查询行政区出错: {e}")
        return []


DISTRICT_SCHEMA = {
    "name_for_human": "行政区划查询",
    "name_for_model": "get_sub_districts",
    "description_for_model": (
        "用于查询中国某个行政区域（省、市、区）下属的次级行政区列表。"
        "当你需要引导用户精确选择位置，或者需要确认某个城市下有哪些区县时使用。"
        "输入一个关键词（如'四川省'或'成都市'），该工具将返回其直接下属的行政区名称列表。"
    ),
    "parameters": [
        {
            "name": "keywords",
            "description": "需要查询的行政区名称，例如：'浙江省'、'杭州市' 或 '西湖区'。",
            "required": True,
            "schema": {"type": "string"},
        }
    ],
}

if __name__ == "__main__":
    districts = get_districts("成都", 1)
    print("查询到的区县：", districts)
