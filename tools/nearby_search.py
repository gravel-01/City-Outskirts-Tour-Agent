import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
MY_KEY = os.getenv("GAODEDITY_API_KEY")
# API调用详解见：https://lbs.amap.com/api/webservice/guide/api-advanced/newpoisearch


def nearby_search(location, keywords="", types="050000", **kwargs):
    """
    location: 经纬度
    keywords: 关键词
    types: 分类码（050000-餐饮, 070000-生活, 120000-住宅）
    """
    params = {
        "key": MY_KEY,
        "location": location,
        "keywords": keywords,
        "types": types,
        "sortrule": kwargs.get("sortrule", "distance"),
        "region": kwargs.get("region"),
        "radius": kwargs.get("radius", 3000),
        "show_fields": "cost,rating,business,tag",
        "page_size": 10,
    }

    # 过滤掉 None 值
    params = {k: v for k, v in params.items() if v is not None}

    url = "https://restapi.amap.com/v5/place/around"

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] == "1" and int(data["count"]) > 0:
            results = []
            for poi in data["pois"]:
                biz = poi.get("business", {})
                results.append(
                    {
                        "名称": poi.get("name"),
                        "评分": poi.get("rating"),
                        "费用": poi.get("cost"),
                        "距离": f"{poi.get('distance')}m",
                        "地址": poi.get("address"),
                        "状态": biz.get("opentime_today", "未知"),
                    }
                )
            return results
        return "在该范围内未找到匹配的结果。"
    except Exception as e:
        return f"接口调用失败: {e}"


def nearby_search_advanced(
    location, keywords="", types="050000", radius=2000, sortrule="distance", page=1
):
    """
    定制化周边搜索：最大化获取商业信息
    """
    url = "https://restapi.amap.com/v5/place/around"

    # 核心：通过 show_fields 指定需要返回的详细字段
    # 开启：cost(人均), rating(评分), business(营业时间/商圈), photos(图片), navi(出入口)
    show_fields = "cost,rating,business,photos,tag,navi,parking_type"

    params = {
        "key": MY_KEY,
        "location": location,
        "keywords": keywords,
        "types": types,
        "radius": radius,
        "sortrule": sortrule,
        "page_size": 10,
        "page_num": page,
        "show_fields": show_fields,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] == "1" and int(data["count"]) > 0:
            custom_results = []
            for poi in data["pois"]:
                # 提取商业信息
                biz = poi.get("business", {})
                # 提取图片（取第一张作为封面）
                photos = poi.get("photos", [])
                cover_image = photos[0].get("url") if photos else None

                # 构造高度定制化的数据结构
                info = {
                    "基本信息": {
                        "名称": poi.get("name"),
                        "类型": poi.get("type"),
                        "距离": f"{poi.get('distance')}米",
                        "评分": poi.get("rating", "暂无评分"),
                        "人均消费": (
                            f"{poi.get('cost')}元" if poi.get("cost") else "未知"
                        ),
                    },
                    "运营状态": {
                        "今日营业时间": biz.get("opentime_today", "未知"),
                        "商圈": biz.get("business_area", "未知"),
                        "特色标签": poi.get("tag", "无"),
                    },
                    "位置详情": {
                        "详细地址": poi.get("address"),
                        "停车场": poi.get("parking_type", "暂无数据"),
                        "经纬度": poi.get("location"),
                    },
                    "图片链接": cover_image,
                }
                custom_results.append(info)
            return custom_results
        return "搜索成功，但范围内没有匹配的结果。"
    except Exception as e:
        return f"接口请求异常: {str(e)}"


NEARBY_SEARCH_SCHEMA = {
    "name_for_human": "多功能周边地点搜索",
    "name_for_model": "search_nearby_poi",
    "description_for_model": (
        "用于在指定经纬度周边搜索餐厅、生活服务或商务住宅等地点。"
        "该工具支持按距离或综合权重排序，并返回评分、人均消费和营业时间。"
    ),
    "parameters": [
        {
            "name": "location",
            "description": "中心点坐标 '经度,纬度'。必填。",
            "required": True,
            "schema": {"type": "string"},
        },
        {
            "name": "keywords",
            "description": "搜索关键词，如'火锅'、'干洗店'、'公寓'。",
            "required": False,
            "schema": {"type": "string"},
        },
        {
            "name": "types",
            "description": (
                "地点分类码，支持多个用'|'分隔。常用码包括："
                "050000 (餐饮服务，用于找饭店)、"
                "070000 (生活服务，用于找超市、理发店、维修点等)、"
                "120000 (商务住宅，用于找公寓、写字楼、酒店)。"
            ),
            "required": False,
            "schema": {"type": "string", "default": "050000"},
        },
        {
            "name": "sortrule",
            "description": "排序规则：'distance'按距离排序（找最近），'weight'综合排序（找最好）。",
            "required": False,
            "schema": {"type": "string", "default": "distance"},
        },
        {
            "name": "radius",
            "description": "搜索半径（米），默认3000。短途步行建议1000。",
            "required": False,
            "schema": {"type": "integer"},
        },
        {
            "name": "region",
            "description": "搜索区划（城市名或adcode），用于限定搜索范围。",
            "required": False,
            "schema": {"type": "string"},
        },
    ],
}

NEARBY_SEARCH_SCHEMA_ADVANCED = {
    "name_for_human": "深度定制周边搜索",
    "name_for_model": "nearby_search_advanced",
    "description_for_model": (
        "在指定经纬度周边搜索地点。该工具已定制化开启了深度商业信息，"
        "返回结果包含：人均消费、实时评分、今日营业时间、所属商圈及停车场类型。"
        "当你需要进行精准推荐（如：找正在营业的店、找性价比高的店、找好停车的店）时必用。"
    ),
    "parameters": [
        {
            "name": "location",
            "description": "中心点坐标，格式为 '经度,纬度'。",
            "required": True,
            "schema": {"type": "string"},
        },
        {
            "name": "keywords",
            "description": "关键词，如'火锅'。可为空。",
            "required": False,
            "schema": {"type": "string"},
        },
        {
            "name": "types",
            "description": "分类码：050000(餐饮), 070000(生活服务), 120000(商务住宅)。",
            "required": False,
            "schema": {"type": "string", "default": "050000"},
        },
        {
            "name": "radius",
            "description": "搜索半径(米)，默认2000。",
            "required": False,
            "schema": {"type": "integer"},
        },
        {
            "name": "sortrule",
            "description": "排序：'distance'(最近), 'weight'(最好)。",
            "required": False,
            "schema": {"type": "string", "default": "distance"},
        },
    ],
}

if __name__ == "__main__":
    test_location = "116.481488,39.990464"  # 北京市中心点
    results = nearby_search(
        location=test_location,
        keywords="川菜",
        types="050000",
        sortrule="distance",
        radius=2000,
    )
    print("搜索结果：")
    for item in results:
        print(item)
