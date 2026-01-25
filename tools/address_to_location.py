import os
import requests
from dotenv import load_dotenv

load_dotenv()
MY_KEY = os.getenv("GAODEDITY_API_KEY")

geo_url = "https://restapi.amap.com/v3/geocode/geo"
around_url = "https://restapi.amap.com/v5/place/around"


def address_to_location(address: str):
    """将粗略地址转为经纬度"""
    params = {"key": MY_KEY, "address": address}
    try:
        response = requests.get(geo_url, params=params)
        data = response.json()
        if data["status"] == "1" and int(data["count"]) > 0:
            # 返回第一个匹配项的经纬度 "121.50,31.24"
            return data["geocodes"][0]["location"]
        return None
    except Exception as e:
        print(f"地理编码出错: {e}")
        return None


GEO_SCHEMA = {
    "name_for_human": "地理编码",
    "name_for_model": "address_to_location",
    "description_for_model": (
        "将人类可读的详细地址或地名（如'北京市朝阳区望京SOHO'）转换为经纬度坐标（如'116.481,39.990'）。"
        "当用户提供了一个具体的地点名称，而你需要调用需要经纬度参数的工具（如周边餐厅搜索）时，必须先调用此工具进行转换。"
    ),
    "parameters": [
        {
            "name": "address",
            "description": "具体的地址信息，越详细解析越准确。例如：'成都市锦江区春熙路' 或 '上海东方明珠'。",
            "required": True,
            "schema": {"type": "string"},
        }
    ],
}


if __name__ == "__main__":
    test_address = "北京市朝阳区望京SOHO"
    location = address_to_location(test_address)
    print(f"地址 '{test_address}' 的经纬度为: {location}")
