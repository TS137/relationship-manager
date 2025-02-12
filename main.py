import json
import requests
import streamlit as st

# 配置 GitHub 相关信息
GITHUB_TOKEN = "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"  
REPO_OWNER = "TS137"  
REPO_NAME = "relationship-manager"  
FILE_PATH = "people_data.json"  

# GitHub API 基础 URL
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

def load_data_from_github():
    """从 GitHub 加载 people_data.json 文件"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        content = data["content"]  # Base64 编码的内容
        decoded_content = base64.b64decode(content).decode("utf-8")
        return json.loads(decoded_content)
    elif response.status_code == 404:
        # 如果文件不存在，返回空列表
        return []
    else:
        st.error(f"无法加载数据：{response.status_code} - {response.text}")
        return []

def save_data_to_github(data):
    """将数据保存到 GitHub 的 people_data.json 文件"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    # 获取当前文件的 SHA（用于更新文件时需要）
    response = requests.get(GITHUB_API_URL, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json().get("sha")

    # 将数据转换为 JSON 格式并编码为 Base64
    content = json.dumps(data, ensure_ascii=False, indent=4)
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": "Update people_data.json",  # 提交信息
        "content": encoded_content,
        "sha": sha,  # 如果文件已存在，则需要提供 SHA
    }

    # 发送请求更新文件
    if sha:
        response = requests.put(GITHUB_API_URL, headers=headers, json=payload)
    else:
        response = requests.put(GITHUB_API_URL, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        st.success("数据已成功保存到 GitHub！")
    else:
        st.error(f"无法保存数据：{response.status_code} - {response.text}")

# 主函数
def main():
    st.title("人情数据管理系统")

    # 加载数据
    people_data = load_data_from_github()

    # 添加人情记录
    st.header("添加新人情记录")
    name = st.text_input("姓名：")
    relationship = st.text_input("关系（如朋友、亲戚等）：")
    event = st.text_input("事件描述：")
    date = st.text_input("日期（格式：YYYY-MM-DD）：")
    amount = st.number_input("金额（正数表示收到，负数表示支出）：", step=0.01)

    if st.button("添加记录"):
        if name and relationship and event and date:
            person = {
                "name": name,
                "relationship": relationship,
                "event": event,
                "date": date,
                "amount": amount,
            }
            people_data.append(person)
            save_data_to_github(people_data)
        else:
            st.error("请填写所有必填字段！")

    # 查看所有人情记录
    st.header("查看所有人情记录")
    if st.button("查看所有记录"):
        if people_data:
            st.write(people_data)
        else:
            st.warning("当前没有人情记录。")

if __name__ == "__main__":
    main()
