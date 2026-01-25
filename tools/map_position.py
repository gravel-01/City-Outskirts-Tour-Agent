import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
MY_KEY = os.getenv("GAODEDITY_API_KEY")


def map_position(locations: list, names: list, zoom: int = None, size: str = "700*400"):
    """
    生成高德静态地图 URL (修复 labels 格式错误 INVALID_PARAMS 20000)
    """
    # 1. 获取 Key
    api_key = os.getenv("GAODEDITY_API_KEY")
    if not api_key:
        return "错误：未检测到 GAODEDITY_API_KEY"

    if not locations or len(locations) < 1:
        return "错误：请提供至少一个坐标点"

    base_url = "https://restapi.amap.com/v3/staticmap"

    # --- 构造 Markers (红点气泡) ---
    marker_groups = []
    for i, loc in enumerate(locations):
        clean_loc = loc.strip()
        label = chr(65 + i) if i < 26 else "Z"
        marker_groups.append(f"mid,0xFF0000,{label}:{clean_loc}")
    markers_str = "|".join(marker_groups)

    # --- 构造 Labels (文字标注) - 【核心修复】 ---
    label_groups = []
    for name, loc in zip(names, locations):
        # 1. 清洗名称：去掉冒号、逗号、竖线，防止破坏格式
        clean_name = (
            name.replace("|", "").replace(":", "").replace(",", "")[:6]
        )  # 限制长度

        # 2. 严格遵循格式：内容,字体,粗体,字号,字色,背景:经纬度
        # 字体:0(微软雅黑), 粗体:1, 字号:14, 字色:0xFFFFFF(白), 背景:0x5288d8(蓝)
        # 注意：这里必须全是逗号，直到最后接经纬度前才用冒号
        style_str = f"{clean_name},0,1,14,0xFFFFFF,0x5288d8"

        label_groups.append(f"{style_str}:{loc.strip()}")

    labels_str = "|".join(label_groups)

    # --- 构造 Paths (连线) ---
    paths_str = ""
    if len(locations) >= 2:
        path_points = ";".join([l.strip() for l in locations])
        paths_str = f"5,0x0000FF,0.8,,:{path_points}"

    # --- 组装参数 ---
    # 使用 urllib.parse.quote 确保参数安全，但我们要手动拼接以防过度转义
    # 这里我们只对 values 做简单的字符串处理，不使用 urlencode 对整体编码，防止 : 被转义
    query_parts = [
        f"key={api_key}",
        f"size={size}",
        f"markers={markers_str}",
        f"labels={labels_str}",
        f"scale=2",
    ]

    if paths_str:
        query_parts.append(f"paths={paths_str}")
    if zoom:
        query_parts.append(f"zoom={zoom}")

    return f"{base_url}?{'&'.join(query_parts)}"


MAP_POSITION = {
    "name_for_human": "高级行程地图",
    "name_for_model": "map_position",
    "description_for_model": (
        "该工具用于生成包含图标(markers)、文字名称标注(labels)和行程路径线(paths)的高级静态地图图片 URL。"
        "适用于：推荐‘一日游’线路、展示‘美食街探店’分布、或为用户规划多个地点间的行走路线。"
        "地图会自动在每个地点标出 A, B, C 气泡，并在旁边显示具体的地点名称，最后按顺序用蓝色线条连接各点。"
    ),
    "parameters": [
        {
            "name": "locations",
            "description": (
                "经纬度坐标列表，需按访问或推荐顺序排列。格式为 '经度,纬度'。"
                "注意：请确保经纬度小数点后不超过6位（例如 '116.481488,39.990464'）。"
            ),
            "required": True,
            "schema": {"type": "array", "items": {"type": "string"}},
        },
        {
            "name": "names",
            "description": (
                "对应的地点名称列表，需与 locations 顺序一一对应。"
                "名称中请避免使用英文冒号(:)、逗号(,)或竖线(|)，这些符号会被自动替换为下划线。"
            ),
            "required": True,
            "schema": {"type": "array", "items": {"type": "string"}},
        },
        {
            "name": "zoom",
            "description": "地图缩放级别(1-17)。如果不确定展示范围，请不要提供此参数，系统将自动适配以包含所有标注点。",
            "required": False,
            "schema": {"type": "integer"},
        },
        {
            "name": "size",
            "description": "地图图片的大小，格式为 '宽*高'，最大支持 '1024*1024'。默认值为 '700*400'。",
            "required": False,
            "schema": {"type": "string", "default": "700*400"},
        },
    ],
}


if __name__ == "__main__":
    # 测试数据
    test_locs = [
        "116.481488123,39.990464123",
        "116.48621,39.990112",
        "116.487812,39.983357",
    ]
    test_names = ["起点:望京SOHO", "中转,奔驰大厦", "终点|凯德MALL"]

    url = map_position(test_locs, test_names)
    print("【修复版 URL】请复制到浏览器测试：")
    print(url)
