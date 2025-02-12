import json
import streamlit as st
import pandas as pd
import plotly.express as px

# 初始化人情数据
people_data = []

def load_data():
    """加载已有的人情数据"""
    global people_data
    try:
        with open("people_data.json", "r", encoding="utf-8") as file:
            people_data = json.load(file)
    except FileNotFoundError:
        people_data = []

def save_data():
    """保存人情数据到文件"""
    with open("people_data.json", "w", encoding="utf-8") as file:
        json.dump(people_data, file, ensure_ascii=False, indent=4)

def add_person(name, relationship, event, date, amount):
    """添加新人情记录"""
    # 检查是否已存在相同姓名
    for person in people_data:
        if person["name"] == name:
            st.warning(f"姓名 '{name}' 已存在！请选择更新或跳过。")
            return

    person = {
        "name": name,
        "relationship": relationship,
        "event": event,
        "date": date,
        "amount": amount
    }
    people_data.append(person)
    save_data()
    st.success(f"已成功添加 {name} 的人情记录！")

def delete_person(name):
    """删除指定姓名的人情记录"""
    global people_data
    initial_length = len(people_data)
    people_data = [person for person in people_data if person["name"] != name]
    if len(people_data) < initial_length:
        save_data()
        st.success(f"已成功删除姓名为 '{name}' 的人情记录！")
    else:
        st.warning(f"未找到姓名为 '{name}' 的人情记录！")

def view_all_people():
    """查看所有人情记录（以高级表格形式显示）"""
    if not people_data:
        st.warning("当前没有人情记录。")
        return

    # 将数据转换为 Pandas DataFrame
    df = pd.DataFrame(people_data)
    st.subheader("所有人情记录")
    
    # 使用 Streamlit 的高级表格组件
    st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)

def search_people(keyword):
    """根据关键词检索人情记录（以高级表格形式显示）"""
    results = [person for person in people_data if keyword.lower() in str(person).lower()]
    if not results:
        st.warning(f"未找到与关键词 '{keyword}' 相关的人情记录。")
        return

    # 将结果转换为 Pandas DataFrame
    df = pd.DataFrame(results)
    st.subheader(f"与关键词 '{keyword}' 相关的人情记录")
    st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)

def generate_charts():
    """生成交互式图表"""
    if not people_data:
        st.warning("当前没有人情记录，无法生成图表。")
        return

    # 将数据转换为 Pandas DataFrame
    df = pd.DataFrame(people_data)

    # 按关系分组统计金额总和
    relationship_summary = df.groupby("relationship")["amount"].sum().reset_index()

    # 按月份统计金额总和
    df['date'] = pd.to_datetime(df['date'])  # 确保日期是 datetime 类型
    df['month'] = df['date'].dt.to_period('M').astype(str)  # 提取年月
    monthly_summary = df.groupby("month")["amount"].sum().reset_index()

    # 绘制关系分布的饼图
    fig1 = px.pie(
        relationship_summary,
        names="relationship",
        values="amount",
        title="按关系统计金额分布",
        hole=0.3
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 绘制每月金额变化的折线图
    fig2 = px.line(
        monthly_summary,
        x="month",
        y="amount",
        title="每月金额变化趋势",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

# 主函数
def main():
    st.title("人情数据管理系统")

    # 加载数据
    load_data()

    # 添加人情记录
    st.header("添加新人情记录")
    name = st.text_input("姓名：")
    relationship = st.text_input("关系（如朋友、亲戚等）：")
    event = st.text_input("事件描述：")
    date = st.text_input("日期（格式：YYYY-MM-DD）：")
    amount = st.number_input("金额（正数表示收到，负数表示支出）：", step=0.01)

    if st.button("添加记录"):
        if name and relationship and event and date:
            add_person(name, relationship, event, date, amount)
        else:
            st.error("请填写所有必填字段！")

    # 删除人情记录
    st.header("删除人情记录")
    delete_name = st.text_input("请输入要删除的姓名：")
    if st.button("删除记录"):
        if delete_name:
            delete_person(delete_name)
        else:
            st.error("请输入要删除的姓名！")

    # 查看所有人情记录
    st.header("查看所有人情记录")
    if st.button("查看所有记录"):
        view_all_people()

    # 检索人情记录
    st.header("检索人情记录")
    keyword = st.text_input("请输入要检索的关键词（如姓名、关系、事件等）：")
    if st.button("检索记录"):
        if keyword:
            search_people(keyword)
        else:
            st.error("关键词不能为空！")

    # 生成图表
    st.header("数据分析与可视化")
    if st.button("生成图表"):
        generate_charts()

if __name__ == "__main__":
    main()