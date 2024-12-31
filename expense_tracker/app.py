from flask import Flask, render_template, request, redirect, url_for, session
from web3 import Web3
import json
from decimal import Decimal

app = Flask(__name__)

app.secret_key = '1223334444'

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))  

# Load the contract ABI and contract adress
with open("ABI.json", "r") as abi_file:
    contract_abi = json.load(abi_file)

contract_address = '0xeBB22C5Af8B9D427E55A7F1847B1DC0177F49F1c'

# Set up the contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Mock expense data
expenses = []

# Define the function to log the expense on the blockchain
def add_expense_to_blockchain(category, description, amount):
    # Log the amount to ensure it's correctly passed
    print(f"Adding expense: Category={category}, Description={description}, Amount={amount} ETH")

    # Prepare the transaction
    account = w3.eth.accounts[0]  
    txn = contract.functions.logExpense(category, description, w3.to_wei(amount, 'ether')).build_transaction({
        'chainId': 1337,  # Ganache chain ID
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account),
    })

    # Log the prepared transaction details to verify
    print(f"Transaction details: {txn}")

    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(txn, 
    private_key="0x4a667a8f7e8fec1488101b9f48d45ccda2e4913b9b3bcb54ea058d7ab55f7a3e")

    # Send the transaction
    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    print(f'Transaction sent: {txn_hash.hex()}')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Validate user credentials
        username = request.form['username']
        password = request.form['password']

        # For now, we assume any credentials are valid
        session['logged_in'] = True
        session['account'] = w3.eth.accounts[0]  # Save the account of the first address

        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/')
def index():
    if 'logged_in' not in session:  # Check if the user is logged in
        return redirect(url_for('login'))  # Redirect to login if not logged in

    account = w3.eth.accounts[0]
    balance_wei = w3.eth.get_balance(account)  # Balance in Wei (the smallest unit of Ether)
    balance = Decimal(w3.from_wei(balance_wei, 'ether'))  # Convert to Ether and ensure it's a Decimal

    # Reset expenses on every page load (simulate initial state for each run)
    expenses.clear()

    # Calculate the total expenses (sum of all logged expenses)
    total_expenses = 0
    for expense in expenses:  # Or use the contract if you're retrieving expenses from the blockchain
        total_expenses += expense['amount']

    # Subtract the total expenses from the balance
    available_balance = balance - Decimal(total_expenses)  # Ensure total_expenses is also Decimal

    return render_template('index.html', balance=available_balance, account=account)


@app.route('/log_expense', methods=['GET', 'POST'])
def log_expense():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        amount = float(request.form['amount'])  # Ensure this is a float

        # Log the amount to verify it's correctly passed
        print(f"Received expense: Category={category}, Description={description}, Amount={amount} ETH")

        # Add the new expense to the list (local in the Flask app)
        expenses.append({'category': category, 'description': description, 'amount': amount})

        # Add the expense data to the blockchain
        add_expense_to_blockchain(category, description, amount)

        return render_template('log_expense.html', success=True)
    return render_template('log_expense.html')

@app.route('/view_expenses', methods=['GET'])
def view_expenses():
    # Retrieve expenses from the blockchain
    expense_count = contract.functions.getExpenseCount().call()  
    formatted_expenses = []

    for i in range(expense_count):
        expense = contract.functions.getExpense(i).call()  
        formatted_expenses.append({
            'category': expense[0],
            'description': expense[1],
            'amount': w3.from_wei(expense[2], 'ether'),  
            'timestamp': expense[3]
        })
    
    return render_template('view_expenses.html', expenses=formatted_expenses)

@app.route('/logout', methods=['POST'])  
def logout():
    if 'logged_in' in session:
        session.pop('logged_in', None)
        session.pop('account', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
