import os
import sys
import time
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from tools.tool import ReactTools


class SystemPromptBuilder:
    def __init__(self):
        self.tools = ReactTools()

    def build_system_prompt(self) -> str:
        """构建系统提示，直接从工具类获取描述"""
        tool_info = []
        for tool in self.tools.toolConfig:
            tool_info.append(
                f"- {tool['name_for_model']}: {tool['description_for_model']}"
            )

        tool_names = [tool["name_for_model"] for tool in self.tools.toolConfig]

        prompt = f"""现在时间是 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}。你是一位智能旅行助手，可以根据用户的要求定制化短途且详细周边游玩，可以推荐城市的游玩路线，范围等。 你可以使用以下工具来获取所需的信息：
{chr(10).join(tool_info)}

请遵循以下 ReAct 模式：

思考：分析问题和需要使用的工具
行动：选择工具 [{', '.join(tool_names)}] 中的一个
行动输入：提供工具的参数
观察：工具返回的结果

你可以重复以上循环，直到获得足够的信息来回答问题。

最终答案：基于所有信息给出最终答案

当开始的对话时，先获取用户的位置，询问用户的具体需求，例如：
- 您想游览哪个区域（如朝阳区、海淀区、东城区等）？
- 您偏好什么类型的活动（如历史文化、自然风光、美食购物、亲子娱乐等）？
- 您计划游玩多长时间（如半天、一天）？
- 您是否有特定的出发地点或交通方式？

开始！"""
        return prompt

    def get_system_prompt(self) -> str:
        return self.build_system_prompt()

    def refresh_system_prompt(self) -> str:
        # TODO: 如果工具列表发生变化，或者用户有特殊需求，可以调用此方法刷新提示
        pass
