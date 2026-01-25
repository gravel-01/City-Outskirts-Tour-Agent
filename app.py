import streamlit as st
import os
import sys
import re
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "core"))

from core.agent import ReactAgent  # 确保路径正确

# 1. 页面配置
st.set_page_config(page_title="灵感旅途", page_icon="🌍", layout="wide")

# 2.1 加载环境变量
load_dotenv()


@st.cache_resource  # 保证 Agent 全局唯一且不重复初始化
def get_agent():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    url = "https://api.deepseek.com/v1"
    return ReactAgent(api_key=api_key, url=url)


def render_assistant_response(text):
    """
    解析 Agent 的回复，如果里面有地图 URL，则渲染成图片组件
    """
    # 【核心修复点 1】修改正则：
    # [^)\s]+ 表示匹配除了 "右括号 )" 和 "空白字符" 之外的所有字符
    # 这样就能把 key=<用户的密钥> 完整抓取下来了
    map_url_pattern = r"(https://restapi\.amap\.com/v3/staticmap\?[^)\s]+)"

    match = re.search(map_url_pattern, text)

    if match:
        full_url = match.group(1)  # 获取匹配到的 URL 完整部分

        # 【核心修复点 2】更强力的 Key 找回机制
        # 只要发现 URL 里包含 <...> 或者 key 不完整，就强行替换
        if "<" in full_url or "key=" not in full_url or "用户的密钥" in full_url:
            # 从环境变量重新获取 Key
            real_key = os.getenv("GAODEDITY_API_KEY")

            if real_key:
                # 情况 A: Agent 把 key 写成了 key=<用户的密钥> -> 正则替换
                if "key=" in full_url:
                    full_url = re.sub(r"key=[^&]*", f"key={real_key}", full_url)
                # 情况 B: Agent 压根没写 key 参数 -> 在末尾补上
                else:
                    full_url += f"&key={real_key}"

            # 打印修复后的 URL 方便调试
            print(f"🔧 [自动修复] 地图 Key 已替换，最终 URL: {full_url}")

        # 将文本中的长 URL 替换为短提示
        clean_text = text.replace(match.group(0), " *(⬇️ 查看下方地图)* ")
        st.markdown(clean_text)

        # 渲染图片
        with st.expander("🗺️ 点击查看推荐位置分布图", expanded=True):
            # width="stretch" 是新版 Streamlit 的写法，防止报错
            st.image(full_url, caption="推荐行程可视化", width="stretch")
    else:
        st.markdown(text)


# 2.2 初始化 Agent和critic Agent
agent = get_agent()
critic_agent = get_agent()

# 3. 初始化 Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 侧边栏
with st.sidebar:
    st.title("⚙️ 控制面板")
    if st.button("清空对话历史"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("### 🤖 状态")
    st.success("Agent 已就绪")

with st.sidebar:
    st.header("📍 精确位置设置")

    # --- 第一步：初始化省市信息（仅在初次加载时执行） ---
    if "init_location" not in st.session_state:
        # 获取初始 IP 定位
        city_info = agent.tools._tools_map["get_city"]()
        st.session_state.init_province = city_info[0]["city"]
        st.session_state.init_city = ""
        st.session_state.init_location = True

    # --- 第二步：层级联动选择器（放在 Form 外，保证实时刷新） ---

    # 1. 省份选择
    provinces = agent.tools._tools_map["get_districts"]("中国", 1)
    try:
        p_index = provinces.index(st.session_state.init_province)
    except:
        p_index = 0
    selected_province = st.selectbox("1. 选择省份", options=provinces, index=p_index)

    # 2. 城市选择 (随省份联动)
    cities = agent.tools._tools_map["get_districts"](selected_province, 1)
    try:
        # 如果是初始状态，尝试定位到 IP 城市
        c_index = cities.index(st.session_state.init_city)
    except:
        c_index = 0
    selected_city = st.selectbox("2. 选择城市", options=cities, index=c_index)

    # 3. 区域选择 (随城市联动)
    districts = agent.tools._tools_map["get_districts"](selected_city, 1)
    selected_district = st.selectbox(
        "3. 选择区域/县", options=districts if districts else ["全境"]
    )

    # --- 第三步：详细地址与确认提交（放在 Form 内） ---
    with st.form("address_form"):
        detail_addr = st.text_input("4. 详细地址", placeholder="如：解放路 108 号")

        # 表单提交按钮
        submit_btn = st.form_submit_button("确认位置并同步给 Assistant", type="primary")

        if submit_btn:
            # 拼接完整地址字符串供地理编码使用
            full_address = (
                f"{selected_province}{selected_city}{selected_district}{detail_addr}"
            )

            # 调用地理编码 API 将文字转为经纬度坐标
            loc_result = agent.tools._tools_map["address_to_location"](full_address)

            if loc_result:
                # 存入 session_state 供整个 App 使用
                st.session_state.location = loc_result
                st.session_state.address_name = full_address
                st.success(f"✅ 定位成功！")
            else:
                st.error("❌ 地址解析失败，请检查详细地址。")

    # 显示当前生效的地址
    if "address_name" in st.session_state:
        st.divider()
        st.info(f"当前服务地址：\n{st.session_state.address_name}")

    # --- 请将此代码段放在 app.py 的侧边栏 (with st.sidebar:) 内部的最下方 ---

    st.markdown("---")
    st.header("🛠️ 调试工具 (Debug)")

    if st.button("开始图片测试"):
        # 测试 1: 加载普通网络图片 (Streamlit 官方 Logo)
        st.subheader("1. 测试普通网络图片")
        try:
            st.image(
                "https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png",
                caption="如果能看到这张图，说明 Streamlit 图片组件正常",
                width="content",
            )  # 注意：这里用 width="content" 兼容旧版本，或者直接去掉 width
            st.success("✅ 普通图片加载成功")
        except Exception as e:
            st.error(f"❌ 普通图片加载失败: {e}")

        # 测试 2: 测试高德静态地图
        st.subheader("2. 测试高德地图 API")

        # 强制重新读取环境变量，防止缓存问题
        load_dotenv(override=True)
        my_key = os.getenv("GAODEDITY_API_KEY")

        if not my_key:
            st.error(
                "❌ 严重错误：未读取到 GAODEDITY_API_KEY！请检查 .env 文件路径或内容。"
            )
        else:
            st.info(f"当前读取到的 Key 前4位: {my_key[:4]}****")

            # 手动构造一个绝对正确的 URL (北京天安门)
            # 这里的参数非常简单，排除复杂参数导致的错误
            test_url = f"https://restapi.amap.com/v3/staticmap?location=116.397428,39.90923&zoom=13&size=700*300&markers=mid,0xFF0000,A:116.397428,39.90923&key={my_key}"

            st.markdown(f"**正在尝试请求的 URL:**")
            st.code(test_url)  # 展示出来，你可以复制到浏览器试试

            try:
                st.image(
                    test_url,
                    caption="如果能看到地图，说明 Key 和 API 正常",
                    use_container_width=True,
                )
                st.success("✅ 高德地图加载成功！问题出在 Agent 生成的 URL 上。")
            except Exception as e:
                st.error(f"❌ 高德地图加载失败: {e}")
                st.warning("请尝试复制上面的 URL 到浏览器中打开，看看报错信息是什么？")

# 5. 主界面
st.title("🌍 灵感旅途")


# 展示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # 【修改点2】如果是 assistant 的消息，使用渲染函数；用户消息保持原样
        if message["role"] == "assistant":
            render_assistant_response(message["content"])
        else:
            st.markdown(message["content"])

# 用户输入
if query := st.chat_input("今天的行程的灵感？"):
    # 1. 展示用户消息
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # --- 【核心修改开始】：构建带上下文的 Prompt ---
    # 如果侧边栏有确定的位置，将其作为系统提示前缀加到 query 中
    context_prefix = ""
    if "address_name" in st.session_state:
        context_prefix = f"【系统提示：用户当前所在的精确位置是：{st.session_state.address_name}。请基于此位置回答。】\n"

    full_prompt = context_prefix + query
    # --- 【核心修改结束】 ---

    # 2. 展示 Assistant 响应
    with st.chat_message("assistant"):
        with st.status("Agent 正在深度思考并调用工具...", expanded=True) as status:
            # 注意：这里传给 Agent 的是 full_prompt (带位置信息)，而不是原始 query
            response_text = agent.run(full_prompt, verbose=True)
            status.update(label="思考完成！", state="complete", expanded=False)

        # 调用渲染函数
        render_assistant_response(response_text)

    # 注意：存入历史记录时，建议只存 response_text，保持纯净
    st.session_state.messages.append({"role": "assistant", "content": response_text})
