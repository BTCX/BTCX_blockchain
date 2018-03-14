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

- [POST /wallet/balance](#post-walletbalance)
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

Request body:

    {
        "transactions":[
            {
                "currency":"btc",
                "address":"2NAiERRHtLevi4uf4iMuDgLoyvAKkg2jVj2",
                "wallet":"primary_btc_receive",
                "amount": 0
            }
        ]
    }

Response body:

    {
        "receives": [
            {
                "currency": "btc",
                "address": "2NAiERRHtLevi4uf4iMuDgLoyvAKkg2jVj2",
                "received": "0.044",
                "risk": "low",
                "txids": [
                    {
                        "txid": "5fcacedef771af8d97f533239cc18e6e7680eg30cdfb26b3e532fc7c1db591dfg",
                        "received": "0.023",
                        "confirmations": 1234,
                        "date": "2018-01-14 03:42:11"
                    },
                    {
                        "txid": "8f75f2c00cb717965f6dc9c1bf70cd089fte2892420dcaad578517b2dc12c956",
                        "received": "0.021",
                        "confirmations": 1234,
                        "date": "2018-02-01 16:23:14"
                    }
                ]
            }
        ],
        "chain": 2,
        "error": 0,
        "error_message": ""
    }

### POST /sendmany

Request body:

    {
        "currency":"btc",
        "toSend": [
            {
                "amount":0.001,
                "toAddress":"2N7nCLKXxWrUEqyZFvt7eahvEaxAZni1fwK"
            },
            {
                "amount":0.002,
                "toAddress":"2NAiERRHtLevi4uf4iMuDgLoyvAKkg2jVj2"
            }
        ],
        "fromAddress":"2N3itqAdDkJNC6aMq2FLaQYnDar1vzzSRFv",
        "txFee":0.0001,
        "wallet":"primary_btc_send"
    }

Response body:

    {
        "txid": "1cd8b891bc0ffb291848f1a2b45b236f0da1b333bdc2124310c106b32b7fb143",
        "status": 200,
        "fee": "0.00004980",
        "message": "Send many is done.",
        "chain": 2,
        "error": 0,
        "error_message": ""
    }
