# Moneropay simulator 

READ BEFORE USING 


This is a standalone flask application that simulates all of the
endpoints that Moneropay server offers. 

This is not a working system. This script is designed to help
developers writing integrations that make use of moneropay. The 
standalone script is helpful in debugging integrations since you don't have to worry about running a full monero node and database. 

The addresses are hardcoded. All interactions are dummy simulated data.

This is a super quick and dirty script. Only reason this is public is in case this helps someone else 
who is developing. 


## Requirements 
pip install flask

## Supported endpoints 

/balance → returns static balances

/health → returns static health info

/receive (POST) → stores “payment requests” in memory and returns a fake subaddress

/receive/<address> (GET) → shows simulated incoming transfers for that subaddress

/transfer (POST) → simulates sending funds and returns fake tx hashes

/transfer/<tx_hash> (GET) → returns info about that transaction

Memory storage simulates callbacks and confirmations.

## How to run 

python3 app.py 


For local curl usage:
set the env variable 
endpoint="http://localhost:5000"

now you can curl with 
curl -s -X GET "${endpoint}/balance"

or for example, to get a new address:
```
curl -s -X POST "${endpoint}/receive"   -H 'Content-Type: application/json'   -d '{"amount": 123000000, "description": "Server expenses", "callback_url": "http://merchant/callback/moneropay_tio2foogaaLo9olaew4o"}'
```





