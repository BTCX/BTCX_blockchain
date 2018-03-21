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
| currency      | String | Specifies the currency for which the balance is returned.  | btc / ltc / bch |

Response parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| wallets               | Array | Holds an array of JSON objects which represents a specific wallet | |
| wallet                | String | Defines the name of the specific wallet  | |
| wallet_type        | String | Defines the wallet type  | receive / send |
| balance             | Float | Specifies balance of the specific wallet | |
| chain                 | Int | Specifies which chain the wallet node is configured for | 0 (Unknown) / 1 (Mainnet) / 2 (Testnet) / 3 (Regtest) |
| error                  | Int | Indicates if an error occurred when requesting the balance for the specific wallet | 0 (No error) / 1 (Error occurred) |
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

Function:

Transfers funds from a specified wallet to a specified address that corresponds to a safe address defined in the config.yml file.


Request parameter/parameters definition:

| Parameter   | Type   | Description | Possible values | Optional |
| --------------| ------  | --------- | --------- | --------- |
| transfers        | Array | Holds an array of JSON objects which represents the different transfers to be executed. Supports multi currency transfers with the same request. | | |
| currency        | String | Specifies the currency of the transfer | btc / ltc / bch | |
| wallet             | String | Specifies which specific wallet will be used when setting the inputs for the transfer transaction | | |
| safe_address | String | Specifies which specific address the transaction outputs will be locked to. The address MUST correspond to an address defined in config file under /btcxblockchainapi/btcxblockchainapi/config.yml. | | |
| amount          | Float | Defines the total amount that will be transferred. NOTE: this amount is the total amount including fees, and the request will therefore fail if the total amount does not exceed the transaction fee.  | | |
| txFee             | Float | Defines the fee used in the highest denominator for the currency. For bitcoin this is in BTC (hence 0.00000001 is one satoshi) per weight for the transaction. Does currently have no effect for Litecoin or Bitcoin Cash, and the fee set by the node is used. | | Yes |

Response parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| transfers            | Array | Holds an array of JSON objects which represents the transfers that were handled of the requested transfers. NOTE: It can occur that a transfer fails when handled. Since the transfer array in the request are looped through and handled through iteration, the iteration may in some rare cases halt when the transfer fails. In such cases, the length of the array of transfers in the response, is shorter than the length of the array in the transfer request.   | |
| currency            | String | Specifies the currency of the specific transfer. | btc / ltc / bch |
| to_address        | String | Specifies to which specific address the transfer output was locked. | |
| amount              | Float | Specifies the total amount of the transaction for the specific transfer. NOTE: This amount is including the fee of the transaction. The fee must therefore be subtracted from the amount to get the actual value that was locked to the to_address  | |
| fee                     | Float | Definies the total fee of the transaction for the specific transfer. This is specified in the highest denominator for the currency. For bitcoin the fee is in BTC (hence 0.00000001 is one satoshi)  | |
| message           | String | Includes a message corresponding how well the transfer was executed | |
| status                | String | Indicates if the transaction of the transfer succeeded or not. | ok / fail |
| txid                    | String | Corresponds to the txid of the transaction of the specific transfer, if it was successful.  | |
| chain                 | Int | Specifies which chain the wallet node is configured for | 0 (Unknown) / 1 (Mainnet) / 2 (Testnet) / 3 (Regtest) |
| error                  | Int | Indicates if an error occurred when requesting the balance for the specific wallet | 0 (No error) / 1 (Error occurred) |
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

Function:

Generates a specified of new addresses for a specified wallet.


Request parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| currency      | String | Specifies which currency the addresses should be generated for. | btc / ltc / bch |
| wallet           | String | Specifies which specific wallet the addresses (and keys corresponding to the addresses) will be generated in.  | |
| quantity       | Int | Defines how many addresses should be generated. | |

Response parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| chain                 | Int                  | Specifies for which chain the wallet node is configured | 0 (Unknown) / 1 (Mainnet) / 2 (Testnet) / 3 (Regtest) |
| addresses         | String Array   | An array of strings where every string represents a generated address. | |
| error                  | Int                  | Indicates if an error occurred when requesting the balance for the specific wallet. | 0 (No error) / 1 (Error occurred) |
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

Function:

Returns all transactions that have been sent to a specific address that is part of the wallet.


Request parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| transactions | JSON Array | And array of JSON objects, where every object represents the received payment to check. Supports multi currency checks. | |
| currency      | String | Specifies which currency the specific received payment should be checked for | btc / ltc / bch |
| address       | String | Defines the address the received payment should be checked for. NOTE: The address must be part of the specified wallet. | |
| wallet           | String | Specifies which specific wallet the address sent in the address parameter should be "stored" (e.g. hold keys that correspond to the address).  | |

Response parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| receives              | JSON Array   | An array that holds JSON objects representing the receive response to the corresponding receive request in the request body "transactions" parameter.  NOTE: It can occur that a receive request fails when handled. Since the "transaction" array in the request are looped through and handled through iteration, the iteration may in some rare cases halt when the receive request fails. In such cases, the length of the array of receive responses in the response, is shorter than the length of the transaction array in the request. |  |
| currency             | String            | Specifies which currency the specific received payment has been checked for. | btc / ltc / bch |
| address              | String            | Defines the address the specific received payment has be checked for.  | |
| received             | String            | The total amount that has been received for the specific address in the highest denominator for the currency. For bitcoin the fee is in BTC (hence 0.00000001 is one satoshi) | |
| risk                     | String            | Indicates if any of the transactions sent to the address is at risk of being forked away (based on number of confirmations). The minimum confirmations required for the specific alternatives is defined in the in config file under /btcxblockchainapi/btcxblockchainapi/config.yml.   | low / medium / high |
| txids                   | JSON Array   | An array of JSON objects where an object holds information regarding an actual transaction that have been broadcasted to the network of a specific cryptocurrency. The transactions in this array represents the transactions sent to the address of the specific received payment response.  | |
| txid                     | String            | The txid of the transaction broadcasted to the network. | |
| received             | String            | The amount of the output locked to the address for the specific transaction | |
| confirmations     | Int                 | Number of confirmations for the specific transaction  | |
| date                   | String            | The date of the specific transaction | |
| chain                 | Int                  | Specifies for which chain the wallet node is configured | 0 (Unknown) / 1 (Mainnet) / 2 (Testnet) / 3 (Regtest) |
| error                  | Int                  | Indicates if an error occurred when requesting the balance for the specific wallet. | 0 (No error) / 1 (Error occurred) |
| error_message  | String            | Holds a descriptive message corresponding to the error.  | |

Request body:

    {
        "transactions":[
            {
                "currency":"btc",
                "address":"2NAiERRHtLevi4uf4iMuDgLoyvAKkg2jVj2",
                "wallet":"primary_btc_receive"
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

Function:

Sends out a specified amount of cryptocurrency to all addresses specified in the request parameters.


Request parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| currency      | String            | Specifies the currency of the sendmany request (Only one currency per request is supported) | btc / ltc / bch |
| toSend        | JSON Array   | An JSON array where every object represents a request to send a specific amount to a specific address | |
| amount        | Float             | The amount to send to the specified address for the specific send request. NOTE: This amount is excluding the transaction fee (the fee will therefore be added to the total transaction) | |
| toAddress    | String           | The address to send the specified amount to for the specific send request. | |
| fromAddress| String           | Specifies the account that funds will be taken from for the entire send many request. | |
| txFee            | Float            | Defines the fee used in the highest denominator for the currency. For bitcoin this is in BTC (hence 0.00000001 is one satoshi) per weight for the transaction. Does currently have no effect for Litecoin or Bitcoin Cash, and the fee set by the node is used.  | |
| wallet           | String           | Specifies which specific wallet the address sent in the address parameter should be "stored" (e.g. hold keys that correspond to the address).  | |

Response parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| txid                     | String            | The txid of the transaction broadcasted to the network. | |
| status                | String             | Indicates if the transaction of the transfer succeeded or not. | 200 / 400 / 406 / 500 |
| fee                     | Float              | Defines the total fee of the sendmany transaction. This is specified in the highest denominator for the currency. For bitcoin the fee is in BTC (hence 0.00000001 is one satoshi)  | |
| message           | String             | Includes a message corresponding how well the transfer was executed | |
| chain                 | Int                  | Specifies for which chain the wallet node is configured | 0 (Unknown) / 1 (Mainnet) / 2 (Testnet) / 3 (Regtest) |
| error                  | Int                  | Indicates if an error occurred when requesting the balance for the specific wallet. | 0 (No error) / 1 (Error occurred) |
| error_message  | String            | Holds a descriptive message corresponding to the error.  | |

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


### POST /wallet_notify

Function:

An endpoint that takes a transaction id that should be called on the triggering of a wallet notify event, for transactions that are received by the wallet that triggers the event.

Request parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| currency      | String            | Specifies the currency the wallet notify event was triggered for. | btc / ltc / bch |
| txid              | String            | Specifies the txid that triggered wallet notify event sent. |  |

Response parameter/parameters definition:

| Parameter   | Type   | Description | Possible values |
| --------------| ------  | --------- | --------- |
| chain                 | Int                  | Specifies for which chain the wallet node is configured | 0 (Unknown) / 1 (Mainnet) / 2 (Testnet) / 3 (Regtest) |
| error                  | Int                  | Indicates if an error occurred when requesting the balance for the specific wallet. | 0 (No error) / 1 (Error occurred) |
| error_message  | String            | Holds a descriptive message corresponding to the error.  | |

Request body:

    {
        "currency":"btc",
        "txid":"e43b1fa2547e814979b7j01346c90gh368279fgcf4123e49r9b61d29tf4923th"
    }

Response body:

    {
        "chain": 2,
        "error": 0,
        "error_message": ""
    }

