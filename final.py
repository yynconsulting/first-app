import spacy
import re

def process_transaction(transaction_input):
    """
    处理用户输入的交易语句并生成相应的会计分录。
    """
    journal_entries = []
    
    # 将输入的交易语句按换行符或句号等分割为多个句子，处理更加灵活
    sentences = re.split(r'[;。]', transaction_input)  # 可以考虑用正则分割多个句子
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        print(f"Processing sentence: {sentence}")
        
        # 提取实体信息
        entities = extract_entities(sentence)
        
        # 根据交易类型调用相应的规则函数
        transaction_type = entities['transaction_type']
        print(f"Transaction type: {transaction_type}")  # 打印交易类型，用于调试
        
        rule_function_name = transaction_rules.get(transaction_type, {}).get('rule')
        
        if rule_function_name:
            # 获取规则函数并调用
            rule_function = globals().get(rule_function_name)
            if rule_function:
                journal_entry = rule_function(entities)  # 生成会计分录
                journal_entries.append(journal_entry)
            else:
                print(f"Rule function '{rule_function_name}' not found.")
        else:
            print(f"Unable to process transaction: {sentence}")

    return journal_entries

# ============================
# 1. 公共属性：税率、支付方式等
# ============================

# 销售税率设置（按州分类）
sales_tax_rate_by_state = {
    'california': 0.0725,  # 7.25% 销售税
    'new york': 0.04,      # 假设纽约销售税4%
    'texas': 0.0625,       # 假设德克萨斯州销售税6.25%
    # 可以继续扩展其他州的税率
}

# 支付方式的关键词（对应的支付方式）
payment_keywords = {
    'cash': ['cash', 'money', 'paid in cash'],
    'bank_transfer': ['bank transfer', 'bank deposit', 'wire transfer'],
    'cheque': ['cheque', 'check'],
    'credit_card': ['credit card', 'card payment'],
    'other': ['other', 'payment method unknown'],
}

# 默认交易属性（可以根据需求调整）
transaction_properties = {
    'state': 'california',  # 默认州为 California
    'not_received': False,  # 默认款项未收到
    'not_paid': False,      # 默认款项已支付
}

# ============================
# 2. 规则字典：交易类型及其规则
# ============================

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

# ============================
# 2. 识别语句：提取关键信息并选择交易规则
# ============================
def extract_entities(sentence):
    """
    使用 spaCy 提取交易语句中的金额、支付方式、州信息，并判断是否已支付款项或未收到款项。
    同时，利用语义分析识别交易类型。
    """
    # 处理句子
    doc = nlp(sentence)  
    entities = {
        'amounts': [],
        'payment_methods': [],
        'state': 'california',  # 默认州为 California
        'not_received': False,  # 默认款项未收到
        'not_paid': False,      # 默认款项已支付
        'transaction_type': 'Unknown'  # 默认交易类型为未知
    }

    # 提取金额
    for ent in doc.ents:
        if ent.label_ == "MONEY":
            entities['amounts'].append(float(ent.text.replace('$', '').replace(',', '')))

    # 查找支付方式
    for method, keywords in payment_keywords.items():
        for keyword in keywords:
            if keyword in sentence.lower():
                if method not in entities['payment_methods']:
                    entities['payment_methods'].append(method)

    # 提取州名，使用正则匹配
    state_keywords = ['california', 'new york', 'texas', 'florida', 'georgia', 'washington', 'oregon']
    for state in state_keywords:
        if re.search(r'\b' + re.escape(state) + r'\b', sentence.lower()):  # 精确匹配州名
            entities['state'] = state
            break

    # 判断是否包含 "not paid" 或 "not received"
    for token in doc:
        if token.text.lower() == 'not' and token.head.lemma_ == 'receive':
            entities['not_received'] = True  # 未收到款项
        elif token.text.lower() == 'not' and token.head.lemma_ == 'pay':
            entities['not_paid'] = True  # 未支付款项

    # 判断交易类型：通过动词、名词和关键词来匹配
    for token in doc:
        if token.pos_ == 'VERB':
            # 销售
            if token.lemma_ in ['sell', 'sales', 'sold']:
                entities['transaction_type'] = 'sales'
            # 采购
            elif token.lemma_ in ['purchase', 'buy', 'procure', 'bought']:
                entities['transaction_type'] = 'purchase'
            # 投资
            elif token.lemma_ in ['invest', 'investment', 'bought shares', 'purchased bonds']:
                entities['transaction_type'] = 'investment'
            # 收款
            elif token.lemma_ in ['received', 'receipt', 'received payment']:
                entities['transaction_type'] = 'receipts'
            # 付款
            elif token.lemma_ in ['pay', 'payment', 'paid']:
                entities['transaction_type'] = 'payments'
            # 租赁
            elif token.lemma_ in ['lease', 'leased', 'rented']:
                entities['transaction_type'] = 'lease_out'
            # 还款
            elif token.lemma_ in ['repay', 'loan repayment', 'pay off loan']:
                entities['transaction_type'] = 'repayment'
            # 捐赠
            elif token.lemma_ in ['donate', 'donation']:
                entities['transaction_type'] = 'donation_received'
            # 政府补助
            elif token.lemma_ in ['grant', 'government subsidy']:
                entities['transaction_type'] = 'government_grant'
    
    return entities


# 交易规则函数（这里只展示销售和采购规则，其他规则类似修改）
#销售交易规则
def sales_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] or ['bank transfer']
    not_received = entities['not_received']
    journal_entry = {}

    for i, amount in enumerate(amounts):
        sales_tax = round(amount * sales_tax_rate_by_state.get(entities['state'], 0), 2)
        counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]

        if not_received:
            journal_entry[f'Debit_{i+1}'] = f"Accounts Receivable {amount + sales_tax}"
            journal_entry[f'Credit_{i+1}'] = f"Sales Revenue {amount}"
            journal_entry[f'Credit_Tax_{i+1}'] = f"Sales Tax Payable {sales_tax}"
        else:
            journal_entry[f'Debit_{i+1}'] = f"{counterpart_account.capitalize()} {amount + sales_tax}"
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


# 租入交易规则
def lease_in_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] or ['bank transfer']
    not_paid = entities['not_paid']
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]

        if not_paid:
            journal_entry[f'Debit_{i+1}'] = f"Lease Expense {amount}"
            journal_entry[f'Credit_{i+1}'] = f"Accounts Payable {amount}"
        else:
            journal_entry[f'Debit_{i+1}'] = f"Lease Expense {amount}"
            journal_entry[f'Credit_{i+1}'] = f"{counterpart_account.capitalize()} {amount}"

    return journal_entry


# 租出交易规则
def lease_out_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] or ['bank transfer']
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]

        journal_entry[f'Debit_{i+1}'] = f"{counterpart_account.capitalize()} {amount}"
        journal_entry[f'Credit_{i+1}'] = f"Lease Income {amount}"

    return journal_entry


# 对外投资交易规则
def investment_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] or ['bank transfer']
    not_paid = entities['not_paid']
    journal_entry = {}

    if not_paid:
        journal_entry['Debit_1'] = f"Investment {sum(amounts)}"
        journal_entry['Credit_1'] = f"Accounts Payable {sum(amounts)}"
    else:
        for i, amount in enumerate(amounts):
            counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]
            journal_entry[f'Debit_{i+1}'] = f"Investment {amount}"
            journal_entry[f'Credit_{i+1}'] = f"{counterpart_account.capitalize()} {amount}"

    return journal_entry


# 筹资交易规则
def fundraising_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] or ['bank transfer']
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]

        journal_entry[f'Debit_{i+1}'] = f"{counterpart_account.capitalize()} {amount}"
        journal_entry[f'Credit_{i+1}'] = f"Loan {amount}"

    return journal_entry


# 还款交易规则
def repayment_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] if entities['payment_methods'] else ['bank transfer']
    journal_entry = {}

    total_amount = sum(amounts)

    for i, amount in enumerate(amounts):
        counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]

        journal_entry[f'Debit_{i+1}'] = f"Loan {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account.capitalize()} {amount}"

    # 仅输出分录部分
    for key, value in journal_entry.items():
        print(f"{key}: {value}")
    
    return journal_entry


# 收款交易规则
def receipts_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] if entities['payment_methods'] else ['bank transfer']
    journal_entry = {}

    total_amount = sum(amounts)

    for i, amount in enumerate(amounts):
        counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]

        journal_entry[f'Debit_{i+1}'] = f"{counterpart_account.capitalize()} {amount}"
        journal_entry[f'Credit_{i+1}'] = f"Accounts Receivable {amount}"

    # 仅输出分录部分
    for key, value in journal_entry.items():
        print(f"{key}: {value}")
    
    return journal_entry


# 付款交易规则
def payments_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] if entities['payment_methods'] else ['bank transfer']
    journal_entry = {}

    total_amount = sum(amounts)

    for i, amount in enumerate(amounts):
        counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]

        journal_entry[f'Debit_{i+1}'] = f"Accounts Payable {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account.capitalize()} {amount}"

    # 仅输出分录部分
    for key, value in journal_entry.items():
        print(f"{key}: {value}")
    
    return journal_entry


# 其他应收类交易规则
def other_receivables_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods'] if entities['payment_methods'] else ['bank transfer']
    journal_entry = {}

    total_amount = sum(amounts)

    for i, amount in enumerate(amounts):
        counterpart_account = payment_methods[i] if i < len(payment_methods) else payment_methods[0]

        journal_entry[f'Debit_{i+1}'] = f"{counterpart_account.capitalize()} {amount}"
        journal_entry[f'Credit_{i+1}'] = f"Other Receivables {amount}"

    # 仅输出分录部分
    for key, value in journal_entry.items():
        print(f"{key}: {value}")
    
    return journal_entry

def repayment_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}
    
    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Loan {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Repayment):")
    print(journal_entry)

def receipts_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Accounts Receivable {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Receipts):")
    print(journal_entry)

def payments_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Accounts Payable {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Payments):")
    print(journal_entry)

def other_receivables_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Other Receivables {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Other Receivables):")
    print(journal_entry)

def other_payables_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Other Payables {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Other Payables):")
    print(journal_entry)

def prepaid_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Prepaid Revenue {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Prepaid):")
    print(journal_entry)

def prepaid_expenses_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Prepaid Expenses {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Prepaid Expenses):")
    print(journal_entry)

def shareholder_investments_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Shareholder Equity {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Shareholder Investments):")
    print(journal_entry)

def shareholder_withdrawals_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Shareholder Equity {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Shareholder Withdrawals):")
    print(journal_entry)

def external_investment_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Investment {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (External Investment):")
    print(journal_entry)

def loan_received_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Loan'
        journal_entry[f'Debit_{i+1}'] = f"Bank Deposit {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Loan Received):")
    print(journal_entry)

def loan_repayment_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Loan {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Loan Repayment):")
    print(journal_entry)

def dividend_payment_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Dividend Payable {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Dividend Payment):")
    print(journal_entry)

def donation_received_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Donation Revenue {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Donation Received):")
    print(journal_entry)

def government_grant_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Government Grant Revenue {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Government Grant):")
    print(journal_entry)

def employee_reimbursement_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Employee Reimbursement {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Employee Reimbursement):")
    print(journal_entry)

def contingent_event_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Contingent Liability {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Contingent Event):")
    print(journal_entry)

def asset_swap_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Cash'
        journal_entry[f'Debit_{i+1}'] = f"Asset Swap {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Asset Swap):")
    print(journal_entry)

def inventory_adjustment_transaction_rules(entities):
    amounts = entities['amounts']
    payment_methods = entities['payment_methods']
    state = entities['state']
    
    journal_entry = {}

    for i, amount in enumerate(amounts):
        counterpart_account = 'Inventory'
        journal_entry[f'Debit_{i+1}'] = f"Inventory {amount}"
        journal_entry[f'Credit_{i+1}'] = f"{counterpart_account} {amount}"

    print("\nGenerated Journal Entry (Inventory Adjustment):")
    print(journal_entry)

# ============================


