import streamlit as st

# Simulate the journal entry generation function
def generate_journal_entries(transaction_details):
    # Here, you can add the logic to process the transactions and generate journal entries
    entries = []
    transactions = transaction_details.split(";")
    
    for transaction in transactions:
        if "sales income" in transaction.lower():
            entries.append("Debit: Cash 5000, Credit: Sales Income 5000")
        elif "purchase" in transaction.lower():
            entries.append("Debit: Purchase Expenses 3000, Credit: Bank Deposit 3000")
    
    return entries

# Streamlit page content
st.title("Intelligent Accounting Software")
st.subheader("Please input the transaction details (use semicolon ; to separate multiple transactions):")

# User input
transaction_input = st.text_input("Enter transaction details", "")

if transaction_input:
    # Generate and display journal entries
    entries = generate_journal_entries(transaction_input)
    for entry in entries:
        st.write(entry)
