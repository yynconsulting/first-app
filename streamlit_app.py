import streamlit as st
import final  # 假设 final.py 包含处理交易的逻辑

# 设置页面标题
st.title("智能记账系统")

# 创建用户输入框
transaction_input = st.text_area("请输入交易详情（支持多条交易，用分号 `;` 分隔）：")

# 提交按钮
if st.button("提交交易"):
    if transaction_input:
        try:
            # 调用 final.py 中的处理函数
            journal_entries = final.process_transaction(transaction_input)
            st.subheader("生成的会计分录：")
            st.json(journal_entries)  # 展示生成的会计分录
        except Exception as e:
            st.error(f"处理交易时发生错误：{e}")
    else:
        st.warning("请输入交易内容！")
