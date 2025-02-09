import spacy
import re
import streamlit as st

# ============================
# 1. 公共属性：全局变量、常量
# ============================

# 销售税率设置
sales_tax_rate_by_state = {
    'california': 0.0725,  # 7.25% 销售税
    'new york': 0.04,      # 假设纽约销售税4%
    'texas': 0.0625,       # 假设德克萨斯州销售税6.25%
}

# 支付方式的关键词
payment_keywords = {
    'cash': ['cash', 'money'],
    'bank_transfer': ['bank transfer', 'bank deposit', 'wire transfer'],
    'cheque': ['cheque', 'check'],
}

# 交易类型规则字典
transaction_rules = {
    'sales': {
        'keywords': ['sold', 'sales', 'payment received', 'goods sold'],
        'main_account': 'Sales Revenue',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'credit',
        'taxable': True,
        'rule': 'sales_transaction_rules'
    },
    'purchase': {
        'keywords': ['purchased', 'buy', 'procure', 'purchase'],
        'main_account': 'Inventory',
        'counterpart_account': 'Bank',
        'debit_credit_direction': 'debit',
        'taxable': False,
        'rule': 'purchase_transaction_rules'
    },
    # 更多交易类型规则...
}

# 加载预训练的spaCy模型
nlp = spacy.load("en_core_web_sm")

# ============================
# 2. 提取交易细节
# ============================
def extract_entities(sentence):
    """
    使用 spaCy 提取交易语句中的金额、支付方式、州信息，并判断是否已支付款项或未收到款项。
    """
    doc = nlp(sentence)  # 使用已加载的 nlp 模型进行处理
    entities = {
        'amounts': [],
        'payment_methods': [],
        'state': 'california',  # 默认州为 California
        'not_received': False,  # 默认款项未收到
        'not_paid': False,      # 默认款项已支付
        'transaction_type': 'Unknown'  # 默认交易类型为未知
    }

    # 提取金额、支付方式等
    for ent in doc.ents:
        if ent.label_ == "MONEY":
            entities['amounts'].append(float(ent.text.replace('$', '').replace(',', '')))
    
    # 查找支付方式
    for method, keywords in payment_keywords.items():
        for keyword in keywords:
            if keyword in sentence.lower():
                entities['payment_methods'].append(method)
    
    # 提取州名
    if 'california' in sentence.lower():
        entities['state'] = 'california'
    elif 'new york' in sentence.lower():
        entities['state'] = 'new york'
    elif 'texas' in sentence.lower():
        entities['state'] = 'texas'

    # 判断交易类型：通过动词或名词来匹配，避免重复关键词的干扰
    for token in doc:
        if token.pos_ == 'VERB':
            if token.lemma_ in ['purchase', 'buy', 'procure']:  # 采购
                entities['transaction_type'] = 'purchase'
            elif token.lemma_ in ['sell', 'sales']:  # 销售
                entities['transaction_type'] = 'sales'
            # 更多的交易类型判断...

    return entities

# ============================
# 销售交易规则（包括税务处理）
# ============================
def sales_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] or ['bank transfer']
    not_received = entities['not_received']
    state = entities['state']
    journal_entry = {}

    for i, amount in enumerate(amounts):
        # 计算销售税
        sales_tax = round(amount * sales_tax_rate_by_state.get(state, 0), 2)
        total_amount = amount + sales_tax  # 总金额 = 销售额 + 销售税
        counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]

        # 销售税处理
        if not_received:
            journal_entry[f'Debit_{i+1}'] = f"Accounts Receivable {total_amount}"
            journal_entry[f'Credit_{i+1}'] = f"Sales Revenue {amount}"
            journal_entry[f'Credit_Tax_{i+1}'] = f"Sales Tax Payable {sales_tax}"
        else:
            journal_entry[f'Debit_{i+1}'] = f"{counterpart_account.capitalize()} {total_amount}"
            journal_entry[f'Credit_{i+1}'] = f"Sales Revenue {amount}"
            journal_entry[f'Credit_Tax_{i+1}'] = f"Sales Tax Payable {sales_tax}"

    return journal_entry

# 采购交易规则
def purchase_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] or ['bank transfer']
    not_paid = entities['not_paid']
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]

        if not_paid:
            journal_entry[f'Debit_{i+1}'] = f"Inventory {amount}"
            journal_entry[f'Credit_{i+1}'] = f"Accounts Payable {amount}"
        else:
            journal_entry[f'Debit_{i+1}'] = f"Inventory {amount}"
            journal_entry[f'Credit_{i+1}'] = f"{counterpart_account.capitalize()} {amount}"

    return journal_entry

# ============================
# Streamlit UI部分
# ============================

# 标题和说明
st.title("Intelligent Accounting Software")
st.subheader("Please input the transaction details (use semicolon ; to separate multiple transactions):")

# 用户输入交易详情
transaction_input = st.text_area("Enter transaction details", "")

# 按钮生成会计分录
if st.button("Generate Journal Entries"):
    if transaction_input:
        journal_entries = []
        sentences = re.split(r'[;。]', transaction_input)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 提取交易细节并匹配交易类型
            entities = extract_entities(sentence)

            # 获取交易类型并调用相应的规则函数
            transaction_type = entities['transaction_type']
            rule_function_name = transaction_rules.get(transaction_type, {}).get('rule')

            if rule_function_name:
                rule_function = globals().get(rule_function_name)
                if rule_function:
                    journal_entry = rule_function(entities)
                    journal_entries.append(journal_entry)
                else:
                    st.error(f"Rule function '{rule_function_name}' not found")
            else:
                st.error(f"Unable to process transaction: {sentence}")

        if journal_entries:
            st.subheader("Generated Journal Entries:")
            for entry in journal_entries:
                st.write(entry)
    else:
        st.warning("Please enter the transaction details.")
