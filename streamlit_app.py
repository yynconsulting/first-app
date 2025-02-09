import streamlit as st

# Simulate the journal entry generation function
def generate_journal_entries(transaction_details):
    entries = []
    transactions = transaction_details.split(";")
    
    for transaction in transactions:
        # Handle sales transaction and received in cash
        if "sold goods" in transaction.lower() and "received in cash" in transaction.lower():
            amount = 100  # Extract amount from the sentence (hardcoded for now)
            entries.append(f"Debit: Cash ${amount}, Credit: Sales Revenue ${amount}")
        # Handle other types of transactions here
        # You can add more conditions to handle different transaction types
        
    return entries

# Streamlit page content
st.title("Intelligent Accounting Software")
st.subheader("Please input the transaction details (use semicolon ; to separate multiple transactions):")

# User input for transactions
transaction_input = st.text_input("Enter transaction details", "")

# Button to generate journal entries
if st.button('Generate Journal Entries'):
    if transaction_input:
        # Generate and display journal entries
        entries = generate_journal_entries(transaction_input)
        st.write("Generated Journal Entries:")
        for entry in entries:
            st.write(entry)
    else:
        st.warning("Please enter the transaction details.")
