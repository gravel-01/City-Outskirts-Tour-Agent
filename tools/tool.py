import json
import os
from typing import List, Dict, Any, Callable
from tools.weather import get_weather, WEATHER_SCHEMA
from tools.google_search import google_search, GOOGLE_SEARCH
from tools.get_city import get_city, CITY_SCHEMA
from tools.get_districts import get_districts, DISTRICT_SCHEMA
from tools.address_to_location import address_to_location, GEO_SCHEMA
from tools.nearby_search import (
    nearby_search,
    nearby_search_advanced,
    NEARBY_SEARCH_SCHEMA,
    NEARBY_SEARCH_SCHEMA_ADVANCED,
)
from tools.map_position import map_position, MAP_POSITION


class ReactTools:
    """
    React Agent 工具类

    为 ReAct Agent 提供标准化的工具接口
    """

    def __init__(self) -> None:
        # 注册工具，后期新增工具只需在这里添加即可
        self._tools_map: Dict[str, Callable] = {
            # FIXME:要注册新的函数注册即可
            "get_weather": get_weather,
            "google_search": google_search,
            "get_city": get_city,
            "get_districts": get_districts,
            "address_to_location": address_to_location,
            "search_nearby_poi": nearby_search,
            "nearby_search_advanced": nearby_search_advanced,
            "map_position": map_position,
        }
        # 注册工具的描述，用于生成prompt
        self.toolConfig = [
            WEATHER_SCHEMA,
            GOOGLE_SEARCH,
            CITY_SCHEMA,
            DISTRICT_SCHEMA,
            GEO_SCHEMA,
            NEARBY_SEARCH_SCHEMA,
            NEARBY_SEARCH_SCHEMA_ADVANCED,
            MAP_POSITION,
        ]

    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """统一的工具执行入口"""
        if tool_name not in self._tools_map:
            return f"错误：工具 {tool_name} 未定义。"
        return self._tools_map[tool_name](**kwargs)

    def get_tool_descriptions(self) -> str:
        """
        将 toolConfig 转换为一段纯文本描述，
        直接塞进 AGENT_SYSTEM_PROMPT 里。
        """
        descriptions = []
        for tool in self.toolConfig:
            desc = f"工具名: {tool['name_for_model']}\n描述: {tool['description_for_model']}\n参数: {tool['parameters']}"
            descriptions.append(desc)
        return "\n\n".join(descriptions)


if __name__ == "__main__":
    Tool = ReactTools()
    print(Tool.get_tool_descriptions())
    print(Tool.execute_tool("get_weather", city="上海"))
    print(Tool.execute_tool("google_search", search_query="Python编程语言的优缺点"))
