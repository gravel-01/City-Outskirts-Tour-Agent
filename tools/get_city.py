import os
import requests

from dotenv import load_dotenv

load_dotenv()
MY_KEY = os.getenv("GAODEDITY_API_KEY")


def get_city(api_key=MY_KEY, **kwargs):
    # 接口地址更换为 v3/ip
    url = f"https://restapi.amap.com/v3/ip?key={api_key}"

    try:
        # 注意：这里没有传 ip 参数，高德会识别你的公网出口 IP
        response = requests.get(url)
        result = response.json()

        if result.get("status") == "1":
            province = result.get("province")
            city = result.get("city")
            adcode = result.get("adcode")
            rectangle = result.get("rectangle")

            # 处理局域网特殊情况
            if province == "局域网" or not city:
                return [{"error": "定位失败", "reason": "局域网环境或无法识别IP"}]

            # 返回结构化的列表
            return [
                {
                    "province": province,
                    "city": city,
                    "adcode": adcode,
                    "location_rectangle": rectangle,
                }
            ]

        else:
            return f"定位失败，原因：{result.get('info')}"

    except Exception as e:
        return f"请求异常: {e}"


CITY_SCHEMA = {
    "name_for_human": "IP定位",
    "name_for_model": "get_city",
    "description_for_model": (
        "通过用户IP自动获取位置。当你需要知道用户所在城市时调用此工具。"
        "该工具返回一个包含字典的列表，格式如下：[{'province': '省份', 'city': '城市名', 'adcode': '城市编码', 'location_rectangle': '范围坐标'}]。"
        "请从中提取 'city' 字段用于天气或餐厅搜索。"
    ),
    "parameters": [],  # 因为不需要输入，所以保持为空
}

# --- 执行部分 ---
if __name__ == "__main__":
    MY_KEY = os.getenv("GAODEDITY_API_KEY")  # <--- 请在此处填写你的 Key

    print("正在扫描周边信号并请求定位信息...")
    location_info = get_city(MY_KEY)[0]["city"]
    print("-" * 30)
    print(location_info)
