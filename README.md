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

Function:

Returns the "balance" for all wallets specified in the config.yml file. The wallet "balance" is defined for all UTXO based currencies as the aggregated value of all UTXO:s that are locked to outputs that the wallet contains keys to spend.


Request parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| currency      | String | Specifies the currency for which the balance is returned  | btc / ltc / bch |

Response parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| wallets               | Array | Holds an array of json objects which represents a specific wallet | |
| wallet_type        | String | Definies the wallet type  | receive / send |
| balance             | Float | Specifies balance of the specific wallet | |
| chain                 | Int | Specifies which chain the wallet node is configured for | 0 (Unknown) / 1 (Mainnet) / 2 (Testnet) / 3 (Regtest) |
| error                  | Int | Indicates if an error occured when requesting the balance for the specific wallet | 0 (No error) / 1 (Error occured) |
| error_message  | String | Holds a descriptive message corresponding to the error  | |



Example:

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

Request parameter/parameters definition:

| Parameter   | Type   | Description | Possible values | Optional |
| --------------| ------  | --------- | --------- | --------- |
| transfers        | Array | Holds an array of json objects which represents the different transfers to be exectued. Supports multi currency transfers with the same request. | | |
| currency        | String | Specifies the currency of the transfer | btc / ltc / bch | |
| wallet             | String | Specifies which specific wallet will be used when setting the inputs for the transfer transaction | | |
| safe_address | String | Specifies which specific address the transaction outputs will be locked to. The address MUST correspond to an address definied in config file under /btcxblockchainapi/btcxblockchainapi/config.yml. | | |
| amount          | Float | Definies the total amount that will be transfered. NOTE: this amount is the total amount including fee:s, and the request will therefore fail if the total amount does not exceed the transaction fee.  | | |
| txFee             | Float | Definies the fee used in BTC (hence 0.00000001 is one satoshi) per weight for the transaction. Does currently have no effect for Litecoin or Bitcoin Cash, and the fee set by the node is used. | | Yes |

Response parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| transfers            | Array | Holds an array of json objects which represents the transfers that were handled of the requested transfers. NOTE: It can occour that transfer fails when handled. Since the transfer array in the request are looped through and handled through iteration, the iteration may in some rare cases halt when the transfer fails. In such cases, the length of the array of transfers in the response, is shorter than the leght of the array in the transfer request.   | |
| currency            | String | Specifies the currency of the specific transfer. | btc / ltc / bch |
| to_address        | String | Specifies to which specific address the transfer output was locked. | |
| amount              | Float | Specifies the total amount of the transaction for the specific transfer. NOTE: This amount is including the fee of the transaction. The fee must therefore be subtracted from the amount to get the actual value that was locked to the to_address  | |
| fee                     | Float | Definies the total fee of the transaction for the specific transfer. The fee is in BTC (hence 0.00000001 is one satoshi)  | |
| message           | String | Includes a message corresponding how well the transfer was executed | |
| status                | String | Indicates if the transaction of the transfer succeeded or not. | ok / fail |
| txid                    | String | Corresponds to the txid of the transaction of the specific transfer, if it was successfull.  | |
| chain                 | Int | Specifies which chain the wallet node is configured for | 0 (Unknown) / 1 (Mainnet) / 2 (Testnet) / 3 (Regtest) |
| error                  | Int | Indicates if an error occured when requesting the balance for the specific wallet | 0 (No error) / 1 (Error occured) |
| error_message  | String | Holds a descriptive message corresponding to the error  | |

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

Request parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| currency      | String | Specifies which currency the addresses should be generated for. | btc / ltc / bch |
| wallet           | String | Specifies which specific wallet the addresses (and keys corresponding to the addresses) will be gererated in.  | |
| quantity       | Int | Definies how many addresses should be generated. | |

Response parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| chain                 | Int                  | Specifies for which chain the wallet node is configured | 0 (Unknown) / 1 (Mainnet) / 2 (Testnet) / 3 (Regtest) |
| addresses         | String Array   | An array of strings where every string represents a generated address. | |
| error                  | Int                  | Indicates if an error occured when requesting the balance for the specific wallet. | 0 (No error) / 1 (Error occured) |
| error_message  | String            | Holds a descriptive message corresponding to the error.  | |

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
