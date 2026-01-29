# 🌍 City Outskirts Tour Agent

> **一个极简的 ReAct Agent 实现，专为 AI Agent 初学者打造的入门 Demo。**

如果你正在寻找通过代码理解 Agent 原理的途径，那么 **City-Outskirts-Tour-Agent** 是你的最佳起点。这不仅仅是一个旅游助手，更是一个展示 LLM 如何思考与行动的教学模版。

### 🚀 为什么选择这个项目？

* **专为新手设计**：剥离了复杂的框架包装，用最直观的代码展示 ReAct (Reasoning + Acting) 核心逻辑。
* **高度可定制**：
    * **角色定义**：在 `core/prompt.py` 中即可修改 System Prompt。例如，我将它设定为“智能旅行助手”，你也可以把它变成“美食侦探”或“历史导游”。
    * **工具扩展**：直接在 `tools/` 目录下添加 Python 函数即可让 Agent 获得新能力。
* **低成本探索**：核心 LLM 选用 DeepSeek，性价比极高，只需几块钱人民币(5块钱的token足够你使用)即可获得充足的 Token 用量。同时，内置的所有工具（如地图检索、周边搜索等）均基于 免费 API 实现。让你在探索 Agent 新世界时，完全无需顾虑成本问题。

---

# 🛠️ 快速开始 
## 项目前期准备
### 1.环境配置
推荐使用 conda 创建隔离环境
```
# 1. 创建环境 (Python 3.10)
conda create -n agent_env python=3.10

# 2. 激活环境
conda activate agent_env

# 3. 安装依赖
pip install -r requirements.txt
```
### 2.配置环境变量
在项目的一级目录下创建.env（和app.py同一个目录）文件。这里我用的是deepseek的llm,如果想换另一个大模型，只需要修改ANY_MODEL_ENDPOINT，和DEEPSEEK_API_KEY即可。
```
# LLM 模型配置 (默认 DeepSeek)
ANY_MODEL_ENDPOINT=https://api.deepseek.com
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# 工具链配置 (免费额度足够使用)
SERPER_API_KEY=your_serper_key
GAODEDITY_API_KEY=your_amap_key
```
🔑 API Key 获取地址：


- DEEPSEEK_API_KEY购买地址：https://platform.deepseek.com/usage
- SERPER_API_KEY（谷歌搜索,2500次免费/月）：https://serper.dev
- GAODEDITY_API_KEY（高德，2000次免费/月）：https://console.amap.com/dev/id/phone

### 3.可视化页面交互
为了提供更直观、流畅的 Agent 交互体验，本项目使用 Streamlit 构建了可视化前端。它能够将 Agent 的“思考-决策-行动”过程清晰地呈现出来，让你告别枯燥的终端命令行，真正“看见” AI 的思维路径。注册页面https://streamlit.io/

## 开始运行你的agent助手吧
打开terminal，执行 
```
streamlit run app.py 
```
终端运行后，浏览器将自动打开 http://localhost:8501
# 🎨 功能展示与交互
本项目使用 Streamlit 构建了可视化的 Web 界面，让 Agent 的思维过程透明化。

当你成功运行将看到类似是界面：
![1](./image/1.png)

## agent:自动定位与手动修正
Agent 会尝试根据 IP 自动定位。如果定位不准，你可以在侧边栏手动修正位置。

代码原理：```用户输入地址 -> 调用高德 API 转经纬度 -> 注入 Prompt 上下文。```

![1](./image/2.png)
![1](./image/3.png)

## 可视化思考过程 (ReAct)
不同于传统的黑盒对话，你可以点击下拉框查看 Agent 的完整思考路径：```思考 -> 行动 -> 观察。```

代码原理：```agent.run() 返回包含中间步骤的日志，前端进行正则解析并渲染。```

为了更好的模拟大模型反思的过程，在调用```agent.run()```函数之后，会返回```最终答案,[经过处理的反思，模型的原生的回复]```你可以选择显示处理后的输出，也可以选择展示更多的信息：
![1](./image/4.png)

## 完整的对话流程
支持多轮对话、地图渲染及最终行程建议：
![1](./image/5.png)

# 📂代码结构：
项目结构清晰，注释详细，适合逐行阅读学习。

```
City-Outskirts-Tour-Agent/
├── app.py                # 🚀 项目启动入口 (Streamlit 前端逻辑)
├── config.py             # ⚙️ 全局配置文件
├── .env                  # 🔑 环境变量 (API Keys，请勿上传到 GitHub)
├── requirements.txt      # 📦 依赖列表
├── core/                 # 🧠 核心逻辑层
│   ├── agent.py          # ReactAgent 类 (Agent 的大脑)
│   ├── prompt.py         # System Prompt (定义 Agent 的人设/Cosplay)
│   ├── llm_client.py     # LLM 调用封装
│   └── parser.py         # 输出解析器 (清洗模型废话，提取 Action)
├── tools/                # 🛠️ 工具箱 (插件层)
│   ├── __init__.py       # 工具注册
│   ├── search_tool.py    # 联网搜索 (Serper)
│   ├── restaurant.py     # 餐饮检索
│   └── weather.py        # 天气查询
├── memory/               # 💾 记忆层 (可选)
│   └── manager.py        # 对话历史管理
└── utils/                # 🔧 通用工具
    └── logger.py         # 日志记录
 ```       