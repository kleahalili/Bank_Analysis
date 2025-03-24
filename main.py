import pandas as pd
import numpy as np
import json

pd.set_option("display.max_columns", None)

# Exc 1
with open("transactions.json") as f:
    data = json.load(f)

transactions = data["transactions"]
# Select only necessary columns
df = pd.DataFrame(transactions)[
    ["account_id", "amount", "date", "original_description"]
]

# print(df.head())

# Exc 2
# df['type'] = df['amount'].apply(lambda x: 'debit' if x < 0 else 'credit')
# For better performance using vectorized operation
df["type"] = np.where(df["amount"] < 0, "debit", "credit")

# print(df.head(20))

# Exc 3
df["date"] = pd.to_datetime(df["date"])

# Filter transactions containing 'starbucks' in the description
starbucks_df = df[
    df["original_description"].str.contains("starbucks", case=False, na=False)
]

# Filter transactions for year 2024
starbucks_df = starbucks_df[starbucks_df["date"].dt.year == 2024]

# starbucks_df = starbucks_df[starbucks_df['date'].dt.year == 2024]
starbucks_spending = starbucks_df[starbucks_df["type"] == "debit"]
starbucks_total = starbucks_spending["amount"].sum()

print(f"Total spent at Starbucks: {starbucks_total}\n")

# Exc 4

# Add a new column 'month' to the DataFrame
df["month"] = df["date"].dt.strftime("%B")

# Filter transactions for January, February, and March
df = df[df["month"].isin(["January", "February", "March"])]

summary = df.groupby(["month", "type"])["amount"].agg(["count", "sum"]).reset_index()

print(f"Monthly Summary of Debits and Credits: {summary}\n")


# #Exc 5
with open("transactions.json") as f:
    accounts = json.load(f)["accounts"]

accounts_df = pd.DataFrame(accounts)
plaid_checking_account_id = accounts_df[
    (accounts_df["name"] == "Plaid Checking") & (accounts_df["mask"] == "0000")
]["account_id"].values[0]
# print(plaid_checking_account_id)
plaid_checking_df = df[df["account_id"] == plaid_checking_account_id]
debits = plaid_checking_df[plaid_checking_df["type"] == "debit"]
plaid_checking_total = debits["amount"].sum()
print(f"Total spent from Plaid Checking (0000): ${-plaid_checking_total}\n")


# #Exc 6

plaid_checking_transactions = df[
    df["account_id"] == plaid_checking_account_id
].sort_values("date")
current_account_balance = accounts_df.loc[
    accounts_df["account_id"] == plaid_checking_account_id, "balances"
].iloc[0]["current"]

# Starting at 0, will add the current account balance at the end
balance = 0
highest = 0
lowest = 0

# Order transactions by date
plaid_checking_transactions = plaid_checking_transactions.sort_values("date")

for amount in plaid_checking_transactions["amount"]:
    balance += amount

    if balance > highest:
        highest = balance

    if balance < lowest:
        lowest = balance

print(f"Highest balance: ${highest + current_account_balance}\n")
print(f"Lowest balance: ${lowest + current_account_balance}\n")

# Exc 7
monthly_balances = {}

# Get all unique accounts
account_ids = df["account_id"].unique()

for account_id in account_ids:
    # Get all transactions for this account
    account_transactions_df = df[df["account_id"] == account_id].copy()

    # Get the current balance for this account from accounts_df
    account_curr_balance = accounts_df.loc[
        accounts_df["account_id"] == account_id, "balances"
    ].iloc[0]["current"]

    print(f"Account ID: {account_id}")
    print(f"Current Balance: {account_curr_balance}")

    # Make sure the transactions are sorted by date
    account_transactions_df.sort_values("date", inplace=True)
    account_transactions_df["cumsum"] = account_transactions_df["amount"].cumsum()

    # Take only the last value of the cumulative sum for each month
    account_transactions_df.set_index("date", inplace=True)
    end_of_month_values_df = account_transactions_df["cumsum"].resample("ME").last()

    # Since we assumed the starting balance is 0, we need to add the current balance to the end of month values
    monthly_balances[account_id] = end_of_month_values_df + account_curr_balance

print("\nMonthly Balances:")
for account_id, monthly_balance in monthly_balances.items():
    print(f"Account ID: {account_id}")
    print(monthly_balance)
