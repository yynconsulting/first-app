import streamlit as st
import final  # 导入你的 `final.py` 处理交易

st.title("智能记账系统")

# 创建用户输入框
transaction_input = st.text_area("请输入交易详情（支持多条交易，用分号 `;` 分隔）:")

# 处理交易
if st.button("提交交易"):
    if transaction_input:
        journal_entries = final.process_transaction(transaction_input)
        st.subheader("生成的会计分录：")
        st.json(journal_entries)
    else:
        st.warning("请输入交易内容！")
