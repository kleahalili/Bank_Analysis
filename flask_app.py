from flask import Flask, request, jsonify
import pandas as pd
import json
import requests

app = Flask(__name__)

# Load transaction data
with open("transactions.json") as f:
    data = json.load(f)

transactions = data["transactions"]
df = pd.DataFrame(transactions)[
    ["account_id", "amount", "date", "original_description"]
]

# -------------------- Exercise 8 --------------------
@app.route("/transaction_filter")
def transaction_filter():
    text = request.args.get("text", "")

    # Bonus: Currency conversion
    currency = request.args.get("currency", "USD").upper()

    if not text:
        return jsonify({"error": "Missing 'text' query parameter"}), 400

    filtered = df[df["original_description"].str.contains(text, case=False, na=False)]
    total_amount = round(filtered["amount"].sum(), 2)

    if currency != "USD":
        try:
            response = requests.get("https://open.er-api.com/v6/latest/USD")
            rate_data = response.json()
        except requests.exceptions.RequestException:
            return jsonify({"error": "Failed to fetch currency rates"}), 500

        try:
            rate = rate_data["rates"][currency]
        except KeyError:
            return jsonify({"error": "Invalid currency code"}), 400

        total_amount = round(total_amount * rate, 2)

    return jsonify({"total_amount": total_amount, "currency": currency, "text": text})


if __name__ == "__main__":
    app.run(port=8081)
