import json5
import re
import time
import os
import sys
from dotenv import load_dotenv
from llm_client import OpenAICompatibleClient
from prompt import SystemPromptBuilder
from parser import ReActParser

sys.path.append(os.path.join("../tools"))
from tools.tool import *


class ReactAgent:
    def __init__(self, api_key: str = "", url: str = "") -> None:
        self.api_key = api_key
        self.tools = ReactTools()
        self.model = OpenAICompatibleClient(
            model="deepseek-chat",
            api_key=api_key,
            base_url=url,
        )
        # 构建系统prompt
        self.prompt_builder = SystemPromptBuilder()
        self.system_prompt = self.prompt_builder.get_system_prompt()

        # 构建正则匹配
        self.parser = ReActParser()

    # 解析大模型的回答
    def _parse_action(self, text: str, verbose: bool = False) -> tuple[str, dict]:
        """现在只需要调用解析器的方法"""
        return self.parser.parse(text, verbose)

    def _execute_action(self, action: str, action_input: dict) -> str:
        """执行指定的行动，使用解耦后的 tools 管理器"""
        # 检查工具是否存在于我们的注册表中
        if action in self.tools._tools_map:
            try:
                # 动态调用工具函数并传入参数
                # 使用 **action_input 将字典解包为命名参数
                results = self.tools.execute_tool(action, **action_input)
                return f"观察：{results}"
            except Exception as e:
                return f"观察：执行工具 {action} 时出错: {str(e)}"

        return f"观察：未知行动 '{action}'，请尝试从已知工具列表中选择。"

    def _format_response(self, response_text: str) -> str:
        """格式化最终响应"""
        if "最终答案：" in response_text:
            return response_text.split("最终答案：")[-1].strip()
        return response_text

    def run(self, query: str, max_iterations: int = 3, verbose: bool = True) -> str:
        """运行 ReAct Agent

        Args:
            query: 用户查询
            max_iterations: 最大迭代次数
            verbose: 是否显示中间执行过程
        """
        chat_history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"问题：{query}"},
        ]

        # 绿色ANSI颜色代码
        GREEN = "\033[92m"
        RESET = "\033[0m"

        if verbose:
            print(f"{GREEN}[ReAct Agent] 开始处理问题: {query}{RESET}")

        for iteration in range(max_iterations):
            if verbose:
                print(f"{GREEN}[ReAct Agent] 第 {iteration + 1} 次思考...{RESET}")

            # 获取模型响应
            response = self.model.generate(chat_history)

            if verbose:
                print(f"{GREEN}[ReAct Agent] 模型响应:\n{response}{RESET}")

            chat_history.append({"role": "assistant", "content": response})
            # 解析行动
            action, action_input = self._parse_action(response, verbose=verbose)

            if not action or action == "最终答案" or "最终答案：" in response:
                final_answer = self._format_response(response)
                if verbose:
                    print(f"{GREEN}[ReAct Agent] 任务完成{RESET}")
                return final_answer

            if verbose:
                print(
                    f"{GREEN}[ReAct Agent] 执行行动: {action} | 参数: {action_input}{RESET}"
                )

            # 执行行动
            observation = self._execute_action(action, action_input)

            if verbose:
                print(f"{GREEN}[ReAct Agent] 观察结果:\n{observation}{RESET}")

            # 更新当前文本以继续对话
            chat_history.append({"role": "user", "content": observation})

        # 达到最大迭代次数，返回当前响应
        if verbose:
            print(f"{GREEN}[ReAct Agent] 达到最大迭代次数，返回当前响应{RESET}")
        return self._format_response(response)


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    url = "https://api.deepseek.com/v1"
    agent = ReactAgent(api_key=api_key, url=url)

    response = agent.run(
        "美国最近一次阅兵的原因有哪些？", max_iterations=3, verbose=True
    )
    print("最终答案：", response)
