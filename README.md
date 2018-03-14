# BTCX Blockchain API

* [Install instructions](#install-instructions)
* [Request & Response Examples](#request--response-examples)

## Install instructions

1. install pip (Strongly recommend to install Anaconda python)
2. Go to the btcxblockchainapi folder
3. make install -> install all required packages for application
4. make initdb  -> init DB
5. cp config.yml_template config.yml
6. configure the rpc server setting in config.yml
7. python manage.py runserver 0.0.0.0:8000  -> start server

## Request & Response Examples

### API Resources

- [POST /wallet/balance](#post-wallet-balance)
- [POST /transfer](#post-transfer)
- [POST /address](#post-address)
- [POST /receive](#post-receive)
- [POST /sendmany](#post-sendmany)

### POST /wallet/balance

Request body:

    {
        "currency":"btc"
    }
    
Response body:

    {
        "wallets": [
            {
                "wallet": "primary_btc_receive",
                "wallet_type": "receive",
                "balance": 0.2,
                "chain": 2,
                "error": 0,
                "error_message": ""
            },
            {
                "wallet": "backup_btc_receive",
                "wallet_type": "receive",
                "balance": 0.127,
                "chain": 2,
                "error": 0,
                "error_message": ""
            },
            {
                "wallet": "primary_btc_send",
                "wallet_type": "send",
                "balance": 0.7,
                "chain": 2,
                "error": 0,
                "error_message": ""
            },
            {
                "wallet": "btc_segwit_test_send",
                "wallet_type": "send",
                "balance": 0.001,
                "chain": 2,
                "error": 0,
                "error_message": ""
            }
        ]
    }

### POST /transfer

Request body:

    {
        "transfers":[
            {
                "currency":"btc",
                "wallet":"primary_btc_receive",
                "safe_address":"2MzmvJ4L5drgV4yjonxgrvpZkEVaySBZr6N",
                "amount":0.123,
                "txFee":0.00123
            }
        ]
    }

Response body:

    {
        "transfers": [
            {
                "currency": "btc",
                "to_address": "2MzmvJ4L5drgV4yjonxgrvpZkEVaySBZr6N",
                "amount": 0.123,
                "fee": 0.00016,
                "message": "Transfer is done",
                "status": "ok",
                "txid": "0dc909844511f8e8e99d04abee8g4e223c4b8cf43584e0899ef2d6c4841aed7f"
            }
        ],
        "chain": 2,
        "error": 0,
        "error_message": ""
    }

### POST /address

Request body:

    {
        "currency":"btc",
        "quantity":3,
        "wallet":"primary_btc_receive"
    }
    
Response body:

    {
        "chain": 2,
        "addresses": [
            "2N3itqAdDkJNC6aMq2FLaQYnDar1vzzSRFv",
            "2N7nCLKXxWrUEqyZFvt7eahvEaxAZni1fwK",
            "2NAiERRHtLevi4uf4iMuDgLoyvAKkg2jVj2"
        ],
        "error": 0,
        "error_message": ""
    }

### POST /receive
Receive text....

### POST /sendmany
Sendmany text....
