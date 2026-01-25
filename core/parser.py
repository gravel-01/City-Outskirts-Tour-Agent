import re
import json5


class ReActParser:
    """
    专门负责解析大模型返回的 ReAct 格式文本
    """

    def __init__(self):
        # 预编译正则，提高多次调用的效率
        self.action_pattern = r"行动[:：]\s*(\w+)"
        self.action_input_pattern = r"行动输入[:：]\s*({.*?}|\{.*?\}|[^\n]*)"

    def parse(self, text: str, verbose: bool = False) -> tuple[str, dict]:
        """
        从文本中提取 Action 和 Action Input
        """
        action_match = re.search(self.action_pattern, text, re.IGNORECASE)
        action_input_match = re.search(self.action_input_pattern, text, re.DOTALL)

        action = action_match.group(1).strip() if action_match else ""
        action_input_str = (
            action_input_match.group(1).strip() if action_input_match else ""
        )

        # 清理和解析JSON
        action_input_dict = {}
        if action_input_str:
            try:
                # 预处理：去掉可能存在的 Markdown 代码块标记
                clean_input = self._clean_markdown(action_input_str)

                if clean_input.startswith("{") and clean_input.endswith("}"):
                    action_input_dict = json5.loads(clean_input)
                else:
                    # 兜底逻辑：处理非 JSON 格式的字符串输入
                    action_input_dict = {"search_query": clean_input.strip("\"'")}
            except Exception as e:
                if verbose:
                    print(f"[ReAct Parser] 解析参数失败: {e}")
                # 最终兜底：将原始字符串设为 search_query
                action_input_dict = {"search_query": action_input_str.strip("\"'")}

        return action, action_input_dict

    def _clean_markdown(self, text: str) -> str:
        """去掉模型输出中可能包含的 ```json ... ``` 标记"""
        text = text.strip()
        if text.startswith("```"):
            # 移除开头的 ```json 或 ```
            text = re.sub(r"^```(?:json)?\s*", "", text)
            # 移除结尾的 ```
            text = re.sub(r"\s*```$", "", text)
        return text.strip()
