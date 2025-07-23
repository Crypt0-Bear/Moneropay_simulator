#!/usr/bin/env python3
#
#  app.py
#  

from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time
import random

#hardcoded address 
XMR_ADDRESSES = [
    "83DiaB6gCGDgq2gq9GKPPzK3pLKqCU1FTAnZmWrA4gjt6dMB6vLFX2iJ3t5dUKabcYRcNLxbfknQM8xkj6GQBBhu9gAkJLG",
    "85Mj6p4ybMRY3HprdShHFE7VtnLtMKWvQDEq9iAHQpHa3h3ARwne9habsyuuXLwnNqS9iRHbArzzdaEr3QVZ4ae23fkQQxr",
    "886unFAJ5HV1wvUH6UP7XvXoWb6hLUhPHGsatdnwAwiXGWiYNrE2vBGifzXB86fGrYcvqvVJVimEuPAhvaCbsdFs7KEhM6F",
    "8A8djAxv5W3c4c5b2pzg28PA2jeTjq6oQ4jVruZDxLwVZydSpzuawkyFM7ibnMxeDvbaAB6Mvg9bnEWfPdZ5whkpTWBWHdr",
    "83df2iY7raJTybEPzaRyPZbdz9C9BiQRpiETwxeKBiZpPeocNoUpSXqSPP1UHYPZTeEoRfrmqC1FYfM2sSwui9DAPGx1r9H",
    "83nLMK6VqFJF8PJxhUdg2acsTu8nwQDES23y6fdjWsVULrdkbkfkX1kgATxr5D3fyVX41JeeJTafX9o4eHfUh5o1NMQnyrR",
    "87bX1UDHitcWYScDtzurLZeEYkaUG5nav2dvUbFq3V8mZxsec1HU1UBhTqHqi5dA4n9LkYzeLPEqC4VteXPGzAH9EwwdFWi",
    "8BLuVnf7xaYQAZwVeA6Gb8F6e54p1jqdv1Y9wJRZDDB33VJdeXjNmgL6wrQxZ51YPHKks7ctbshNCPRwoSv7L3jPHiUMjbk",
    "832miqegEAxbXWqe2zuBatj7TtReTU3aGFViaLNJ3HGF1ZYx3HvaDWNEjZkKVtHb5h5vYkzwgEtFxHBVWWRkYE2t4a2BsnG"
    ]

TX_HASH = "0c9a7b40b15596fa9a06ba32463a19d781c075120bb59ab5e4ed2a97ab3b7f33"

def get_address():
    random_address = random.choice(XMR_ADDRESSES)
    return random_address

CALLBACK_DEFAULT = "http://merchant/callback"
PORT = 5000


app = Flask(__name__)

# Memory stores
receive_requests = {}   # address -> dict
transfers = {}          # tx_hash -> dict

# Fake balance state
wallet_balance_total = 2513444800
wallet_balance_unlocked = 800000000

# Health simulation
services_status = {
    "walletrpc": True,
    "postgresql": True
}


#The callback managing function (Not really implemented yet)
def execute_callback(_data):
    data = _data
    # simulate callback POST
    print(f"[Callback simulation] POST to {data['callback_url']} with payload:")
    print({
        "amount": data["amount"],
        "complete": True,
        "description": data.get("description", ""),
        "created_at": data["created_at"],
        "transaction": data["transactions"][0]
    })



# Background thread to simulate confirmations
def simulate_confirmations():
    while True:
        time.sleep(5)
        for addr, data in list(receive_requests.items()):
            if not data.get("complete"):
                # simulate enough confirmations
                data["transactions"][0]["confirmations"] += 2
                if data["transactions"][0]["confirmations"] >= 10:
                    data["complete"] = True
                    data["amount"]["covered"]["unlocked"] = data["amount"]["expected"]
                    data["transactions"][0]["locked"] = False
                    # simulate callback POST
                    execute_callback(data)


threading.Thread(target=simulate_confirmations, daemon=True).start()


# ------------------- Endpoints -------------------

@app.route("/balance", methods=["GET"])
def balance():
    return jsonify({
        "total": wallet_balance_total,
        "unlocked": wallet_balance_unlocked
    })


@app.route("/health", methods=["GET"])
def health():
    if all(services_status.values()):
        return jsonify({"status": 200, "services": services_status}), 200
    else:
        return jsonify({"status": 503, "services": services_status}), 503


@app.route("/receive", methods=["POST"])
def receive():
    data = request.get_json()
    amount = data.get("amount")
    description = data.get("description", "")
    callback_url = data.get("callback_url", CALLBACK_DEFAULT)

    # Simulate creating a new subaddress
    subaddress = get_address()
    created_at = datetime.utcnow().isoformat() + "Z"

    # Simulate initial transaction (0 confirmations)
    tx = {
        "amount": amount,
        "confirmations": 0,
        "double_spend_seen": False,
        "fee": 9200000,
        "height": 2402648,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tx_hash": TX_HASH,
        "unlock_time": 0,
        "locked": True
    }

    receive_requests[subaddress] = {
        "address": subaddress,
        "amount": {
            "expected": amount,
            "covered": {"total": 0, "unlocked": 0}
        },
        "description": description,
        "created_at": created_at,
        "transactions": [tx],
        "callback_url": callback_url,
        "complete": False
    }

    return jsonify({
        "address": subaddress,
        "amount": amount,
        "description": description,
        "created_at": created_at
    })


@app.route("/receive/<address>", methods=["GET"])
def receive_status(address):
    entry = receive_requests.get(address)
    if not entry:
        return jsonify({"error": "address not found"}), 404
    return jsonify({
        "amount": entry["amount"],
        "complete": entry["complete"],
        "description": entry["description"],
        "created_at": entry["created_at"],
        "transactions": entry["transactions"]
    })


@app.route("/transfer", methods=["POST"])
def transfer():
    data = request.get_json()
    destinations = data.get("destinations", [])

    tx_hash = uuid.uuid4().hex
    created_at = datetime.utcnow().isoformat() + "Z"
    total_amount = sum(d["amount"] for d in destinations)
    fee = 87438594

    transfers[tx_hash] = {
        "amount": total_amount,
        "fee": fee,
        "state": "completed",
        "transfer": destinations,
        "confirmations": 0,
        "double_spend_seen": False,
        "height": 2407445,
        "timestamp": created_at,
        "unlock_time": 10,
        "tx_hash": tx_hash
    }

    return jsonify({
        "amount": total_amount,
        "fee": fee,
        "tx_hash": tx_hash,
        "tx_hash_list": [tx_hash],
        "destinations": destinations
    })


@app.route("/transfer/<tx_hash>", methods=["GET"])
def transfer_status(tx_hash):
    tx = transfers.get(tx_hash)
    if not tx:
        return jsonify({"error": "tx not found"}), 404
    return jsonify(tx)


# ------------------- Main -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
