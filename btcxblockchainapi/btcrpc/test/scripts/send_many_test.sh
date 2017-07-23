#!/bin/bash
curl -u xxxxx:xxxx -X POST -H 'Content-Type: application/json' -d '{ "currency": "btc", "toSend":
[{ "amount": 0.00004745, "toAddress": "mrVjXCfSQPMgPM79xBtQD9MCFbPeuLj2R6" }],
"fromAddress": "n4avR2NGpEdRejSu9CoiNSfgmTzWngpFo2", "txFee": 0.00260000, "wallet": "send" }' \
 http://127.0.0.1:8000/api/v1/sendmany/