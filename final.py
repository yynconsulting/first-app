import re
import streamlit as st
import spacy
import os

# 加载spaCy模型
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# 交易类型列表
TRANSACTION_TYPES = [
    'sales', 'purchase', 'lease_out', 'lease_in', 'investment', 'fundraising', 
    'repayment', 'receipts', 'payments', 'other_receivables', 'other_payables',
    'prepaid', 'prepaid_expenses', 'shareholder_investments', 'shareholder_withdrawals', 
    'external_investment', 'loan_received', 'loan_repayment', 'dividend_payment',
    'donation_received', 'government_grant', 'employee_reimbursement', 'contingent_event',
    'asset_swap', 'inventory_adjustment'
]

# 销售税率设置（按州分类）
sales_tax_rate_by_state = {
    'california': 0.0725,
    'new york': 0.04,
    'texas': 0.0625,
}

# 交易规则字典
transaction_rules = {
    'sales': {'keywords': ['sold', 'sales', 'payment received', 'goods sold'], 'main_account': 'Sales Revenue', 'taxable': True},
    'purchase': {'keywords': ['purchased', 'buy', 'procure', 'purchase'], 'main_account': 'Inventory', 'taxable': False},
    'lease_out': {'keywords': ['leased out', 'lease income', 'rented out'], 'main_account': 'Lease Income', 'taxable': False},
    # 其他规则同上，省略
}

# 默认货币
CURRENCY = "USD"

# 根据州名返回相应的税率
def get_tax_rate(state):
    """
    根据州名返回相应的税率
    """
    return sales_tax_rate_by_state.get(state.lower(), 0)  # 默认无税

def extract_entities(sentence):
    """
    提取交易语句中的关键信息（如交易类型和金额）
    """
    entities = {'transaction_type': '', 'amount': 0, 'state': ''}

    # 使用 spaCy 进行命名实体识别（NER）
    doc = nlp(sentence)
    
    # 假设交易类型是 TRANSACTION_TYPES 中预定义的类型
    for token in doc:
        if token.text.lower() in [t.lower() for t in TRANSACTION_TYPES]:  # 匹配交易类型
            entities['transaction_type'] = token.text

    # 假设金额是数字
    for ent in doc.ents:
        if ent.label_ == 'MONEY':  # 提取金额实体
            entities['amount'] = float(ent.text.replace(',', '').replace('USD', '').strip())

    # 提取州信息
    for token in doc:
        if token.text.lower() in sales_tax_rate_by_state.keys():  # 如果token是州名
            entities['state'] = token.text

    return entities

def process_transaction(transaction_input):
    """
    处理用户输入的交易语句并生成相应的会计分录
    """
    journal_entries = []

    # 将输入的交易语句按句号或其他分隔符分割成多个句子
    sentences = re.split(r'[;，。]', transaction_input)  # 使用正则分割多个句子
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # 提取实体信息
        entities = extract_entities(sentence)
        
        transaction_type = entities['transaction_type']
        state = entities['state'] or "california"  # 默认使用加州
        tax_rate = get_tax_rate(state)  # 获取州的税率

        # 获取交易规则
        rule = transaction_rules.get(transaction_type.lower())
        if rule:
            main_account = rule.get('main_account')
            taxable = rule.get('taxable', False)

            if taxable:
                # 如果是销售交易，计算销售税
                tax_amount = entities['amount'] * tax_rate
                journal_entries.append({"debit": main_account, "credit": "Tax Payable", "amount": tax_amount})
                entities['amount'] -= tax_amount  # 减去税额

            journal_entries.append({"debit": "Bank Deposit", "credit": main_account, "amount": entities['amount']})
        else:
            st.write(f"Unable to process transaction: {sentence}")

    return journal_entries

# Streamlit UI部分
st.title('Intelligent Accounting Software')
st.write('Please input the transaction information, and the system will automatically generate journal entries.')

# 用户输入的交易语句
transaction_input = st.text_area("Enter transaction details", "")

if transaction_input:
    journal_entries = process_transaction(transaction_input)
    if journal_entries:
        st.write("Generated Journal Entries:")
        st.write(journal_entries)

# 交易规则字典：交易类型及其规则
transaction_rules = {
    'sales': {
        'keywords': ['sold', 'sales', 'payment received', 'goods sold'],
        'main_account': 'Sales Revenue',
        'counterpart_account': None,
        'debit_credit_direction': 'credit',  # 销售是贷方
        'taxable': True,  # 销售涉及税务
        'rule': 'sales_transaction_rules'
    },
    'purchase': {
        'keywords': ['purchased', 'buy', 'procure', 'purchase'],
        'main_account': 'Inventory',
        'counterpart_account': None,
        'debit_credit_direction': 'debit',  # 采购是借方
        'taxable': False,  # 采购不涉及税务
        'rule': 'purchase_transaction_rules'
    },
    'lease_out': {
        'keywords': ['leased out', 'lease income', 'rented out', 'rent income'],
        'main_account': 'Lease Income',
        'counterpart_account': None,
        'debit_credit_direction': 'credit',  # 出租收入是贷方
        'taxable': False,  # 出租收入不涉及税务
        'rule': 'lease_out_transaction_rules'
    },
    'lease_in': {
        'keywords': ['leased', 'lease expense', 'rented', 'rent expense'],
        'main_account': 'Lease Expense',
        'counterpart_account': None,
        'debit_credit_direction': 'debit',  # 租赁支出是借方
        'taxable': False,  # 租赁不涉及税务
        'rule': 'lease_in_transaction_rules'
    },
    'investment': {
        'keywords': ['invested', 'investment', 'purchased shares', 'bought bonds'],
        'main_account': 'Investment',
        'counterpart_account': None,
        'debit_credit_direction': 'debit',  # 投资是借方
        'taxable': False,  # 投资不涉及税务
        'rule': 'investment_transaction_rules'
    },
    'fundraising': {
        'keywords': ['fundraise', 'fundraising', 'raise funds', 'loan'],
        'main_account': 'Fundraising',
        'counterpart_account': None,
        'debit_credit_direction': 'credit',  # 筹资是贷方
        'taxable': False,  # 筹资不涉及税务
        'rule': 'fundraising_transaction_rules'
    },
    'repayment': {
        'keywords': ['repaid', 'repayment', 'loan repayment', 'pay off'],
        'main_account': 'Loan Payable',
        'counterpart_account': None,
        'debit_credit_direction': 'debit',  # 还款是借方
        'taxable': False,  # 还款不涉及税务
        'rule': 'repayment_transaction_rules'
    },
    'receipts': {
        'keywords': ['received', 'receipts', 'payment received'],
        'main_account': 'Accounts Receivable',
        'counterpart_account': None,
        'debit_credit_direction': 'credit',  # 收款是贷方
        'taxable': False,  # 收款不涉及税务
        'rule': 'receipts_transaction_rules'
    },
    'payments': {
        'keywords': ['paid', 'payment', 'pay'],
        'main_account': 'Accounts Payable',
        'counterpart_account': None,
        'debit_credit_direction': 'debit',  # 付款是借方
        'taxable': False,  # 付款不涉及税务
        'rule': 'payments_transaction_rules'
    },
    'other_receivables': {
        'keywords': ['other receivables', 'received', 'accounts receivable'],
        'main_account': 'Other Receivables',
        'counterpart_account': None,
        'debit_credit_direction': 'credit',  # 其他应收是贷方
        'taxable': False,  # 其他应收不涉及税务
        'rule': 'other_receivables_transaction_rules'
    },
    'other_payables': {
        'keywords': ['other payables', 'accounts payable'],
        'main_account': 'Other Payables',
        'counterpart_account': None,
        'debit_credit_direction': 'debit',  # 其他应付是借方
        'taxable': False,  # 其他应付不涉及税务
        'rule': 'other_payables_transaction_rules'
    },
    'prepaid': {
        'keywords': ['prepaid'],
        'main_account': 'Prepaid Revenue',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'credit',  # 预收收入是贷方
        'taxable': False,  # 预收收入不涉及税务
        'rule': 'prepaid_transaction_rules'
    },
    'prepaid_expenses': {
        'keywords': ['prepaid expenses'],
        'main_account': 'Prepaid Expenses',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'debit',  # 预付费用是借方
        'taxable': False,  # 预付费用不涉及税务
        'rule': 'prepaid_expenses_transaction_rules'
    },
    'shareholder_investments': {
        'keywords': ['invest', 'shareholder investment'],
        'main_account': 'Shareholder Equity',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'debit',  # 股东投资是借方
        'taxable': False,  # 股东投资不涉及税务
        'rule': 'shareholder_investments_transaction_rules'
    },
    'shareholder_withdrawals': {
        'keywords': ['shareholder withdrawal'],
        'main_account': 'Shareholder Equity',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'credit',  # 股东提款是贷方
        'taxable': False,  # 股东提款不涉及税务
        'rule': 'shareholder_withdrawals_transaction_rules'
    },
    'external_investment': {
        'keywords': ['external investment'],
        'main_account': 'Investment',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'debit',  # 外部投资是借方
        'taxable': False,  # 外部投资不涉及税务
        'rule': 'external_investment_transaction_rules'
    },
    'loan_received': {
        'keywords': ['loan received'],
        'main_account': 'Bank Deposit',
        'counterpart_account': 'Loan',
        'debit_credit_direction': 'debit',  # 贷款收到是借方
        'taxable': False,  # 贷款不涉及税务
        'rule': 'loan_received_transaction_rules'
    },
    'loan_repayment': {
        'keywords': ['loan repayment'],
        'main_account': 'Loan',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'debit',  # 贷款还款是借方
        'taxable': False,  # 贷款还款不涉及税务
        'rule': 'loan_repayment_transaction_rules'
    },
    'dividend_payment': {
        'keywords': ['dividend payment'],
        'main_account': 'Dividend Payable',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'debit',  # 股息支付是借方
        'taxable': False,  # 股息支付不涉及税务
        'rule': 'dividend_payment_transaction_rules'
    },
    'donation_received': {
        'keywords': ['donation received'],
        'main_account': 'Donation Revenue',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'debit',  # 捐赠收入是借方
        'taxable': False,  # 捐赠收入不涉及税务
        'rule': 'donation_received_transaction_rules'
    },
    'government_grant': {
        'keywords': ['government grant'],
        'main_account': 'Government Grant Revenue',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'debit',  # 政府补助收入是借方
        'taxable': False,  # 政府补助收入不涉及税务
        'rule': 'government_grant_transaction_rules'
    },
    'employee_reimbursement': {
        'keywords': ['employee reimbursement'],
        'main_account': 'Employee Reimbursement',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'debit',  # 员工报销是借方
        'taxable': False,  # 员工报销不涉及税务
        'rule': 'employee_reimbursement_transaction_rules'
    },
    'contingent_event': {
        'keywords': ['contingent event'],
        'main_account': 'Contingent Liability',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'debit',  # 或有事项是借方
        'taxable': False,  # 或有事项不涉及税务
        'rule': 'contingent_event_transaction_rules'
    },
    'asset_swap': {
        'keywords': ['asset swap'],
        'main_account': 'Asset Swap',
        'counterpart_account': 'Cash',
        'debit_credit_direction': 'debit',  # 资产交换是借方
        'taxable': False,  # 资产交换不涉及税务
        'rule': 'asset_swap_transaction_rules'
    },
    'inventory_adjustment': {
        'keywords': ['inventory adjustment'],
        'main_account': 'Inventory',
        'counterpart_account': 'Inventory',
        'debit_credit_direction': 'debit',  # 库存调整是借方
        'taxable': False,  # 库存调整不涉及税务
        'rule': 'inventory_adjustment_transaction_rules'
    }
}
def extract_entities(sentence):
    """
    提取交易语句中的关键信息（如交易类型和金额）
    """
    entities = {'transaction_type': '', 'amount': 0}

    # 使用 spaCy 进行命名实体识别（NER）
    doc = nlp(sentence)
    
    # 假设交易类型是 TRANSACTION_TYPES 中预定义的类型
    for token in doc:
        if token.text.lower() in [t.lower() for t in TRANSACTION_TYPES]:  # 匹配交易类型
            entities['transaction_type'] = token.text

    # 假设金额是数字
    for ent in doc.ents:
        if ent.label_ == 'MONEY':  # 提取金额实体
            entities['amount'] = float(ent.text.replace(',', '').replace('USD', '').strip())

    return entities

def process_transaction(transaction_input):
    """
    处理用户输入的交易语句并生成相应的会计分录
    """
    journal_entries = []
    
    # 将输入的交易语句按句号或其他分隔符分割成多个句子
    sentences = re.split(r'[;。]', transaction_input)  # 使用正则分割多个句子
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # 打印正在处理的句子
        st.write(f"Processing sentence: {sentence}")
        
        # 提取实体信息
        entities = extract_entities(sentence)
        
        # 根据交易类型调用相应的规则函数
        transaction_type = entities['transaction_type']
        st.write(f"Transaction type: {transaction_type}")  # 打印交易类型，用于调试
        
        # 获取规则函数名称
        rule_function_name = transaction_rules.get(transaction_type.lower(), {}).get('rule')
        
        if rule_function_name:
            # 获取并调用规则函数
            rule_function = globals().get(rule_function_name)
            if rule_function:
                journal_entry = rule_function(entities)  # 生成会计分录
                journal_entries.append(journal_entry)
            else:
                st.write(f"Rule function '{rule_function_name}' not found.")
        else:
            st.write(f"Unable to process transaction: {sentence}")

    return journal_entries

# 已经定义了各个交易规则的函数，如 sales_transaction_rules, purchase_transaction_rules 等
# 删除重复的规则函数定义部分
