from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from pprint import pprint
import time
from datetime import datetime
import sys, os
import pickle
from influxdb import InfluxDBClient

rpc_user = "bitcoinrpc"
rpc_pass = "LCT9vuE03S7kRWAxLDCNn4RkNAj6UG9a6RgnlcaM72O4"
rpc_host = "bitcoind"

# 10分に1ブロック平均で生成される(ように難易度が調整される)
# 直近何ブロックを対象とするか
BLOCK_OFFSET = 8
pickle_file = "/data/block_values.pickle"


rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_pass}@{rpc_host}:8332", timeout=240)

rich_addrs_table = {
    "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo": "Binance-coldwallet",
    "bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97": "Bitfinex-coldwallet",
    "1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ": "unknown wallet",
    "35hK24tcLEWcgNA4JxpvbkNkoAcDGqQPsP": "Huobi-coldwallet",
    "37XuVSEpWW4trkfmvWzegTHQt7BdktSKUs": "unknown wallet",
    "38UmuUqPCrFmQo4khkomQwZ4VbY2nZMJ67": "OKEX-coldwallet",
    "1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF": "unknown wallet",
    "3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb": "unknown wallet",
    "bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6": "unknown wallet",
    "3Kzh9qAqVWQhEsfQz7zEQL1EuSx5tyNLNS": "OKEX-coldwallet",
    "3LQeSjqS5aXJVCDGSHPR88QvjheTwrhP8N": "unknown wallet",
    "1LdRcdxfbSnmCYYNdeYpUnztiYzVfBEQeC": "unknown wallet",
    "1AC4fMwgY8j9onSbXEWeH6Zan8QGMSdmtA": "unknown wallet",
    "bc1q5pucatprjrqltdp58f92mhqkfuvwpa43vhsjwpxlryude0plzyhqjkqazp": "wallet: 74771965",
    "1LruNZjwamWJXThX2Y8C2d47QqhAkkc5os": "unknown wallet",
    "3FGKwP7XQA9Gb27if7zQGJSSynbzWLrV3p": "unknown wallet",
    "385cR5DM96n1HvBDMzLHPYcw89fZAXULJP": "Bittrex-coldwallet",
    "3Gpex6g5FPmYWm26myFq7dW12ntd8zMcCY": "unknown wallet",
    "bc1q5shngj24323nsrmxv99st02na6srekfctt30ch": "unknown wallet",
    "36KAwNUR8VeLpUfGwdk7LEN6F4yvoRWMjn": "wallet: 57107814",
    "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s": "Binance-wallet",
    "3D8qAoMkZ8F1b42btt2Mn5TyN7sWfa434A": "unknown wallet",
    "17hf5H8D6Yc4B7zHEg3orAtKn7Jhme7Adx": "unknown wallet",
    "3EBpAZUAW5Tzyd2FhmmUZnYgftxJkKSLmJ": "unknown wallet",
    "3LCGsSmfr24demGvriN4e3ft8wEcDuHFqh": "CoinCheck",
    "12XqeqZRVkBDgmPLVY4ZC6Y4ruUUEug8Fx": "unknown wallet",
    "12ib7dApVFvg82TXKycWBNpN8kFyiAN1dr": "wallet: 967",
    "bc1qvpgyac88vqtslewxu7yu9dqwp8rd83zch55zpm3xgn3mgg72w3kqv0s8qa": "wallet: 74771965",
    "3FpYfDGJSdkMAvZvCrwPHDqdmGqUkTsJys": "wallet: 68880850",
    "12tkqA9xSoowkzoERHMWNKsTey55YEBqkv": "unknown wallet",
    "39WQqCosC8ZD4S9XBPHRnnRUeVRvNctnnm": "unknown wallet",
    "17MWdxfjPYP2PYhdy885QtihfbW181r1rn": "unknown wallet",
    "19D5J8c59P2bAkWKvxSYw8scD3KUNWoZ1C": "unknown wallet",
    "1AnwDVbwsLBVwRfqN2x9Eo4YEJSPXo2cwG": "wallet: Kraken.com",
    "1932eKraQ3Ad9MeNBHb14WFQbNrLaKeEpT": "unknown wallet",
    "1MDq7zyLw6oKichbFiDDZ3aaK59byc6CT8": "unknown wallet",
    "14eQD1QQb8QFVG8YFwGz7skyzsvBLWLwJS": "Kraken.com",
    "1aXzEKiDJKzkPxTZy9zGc3y1nCDwDPub2": "wallet: 30100391",
    "3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE": "OKEX-coldwallet",
    "3ByyPAZmzANfV1sMALVU8zdorPUHEbkZZi": "unknown wallet",
    "3HSMPBUuAPQf6CU5B3qa6fALrrZXswHaF1": "OKEX-coldwallet",
    "bc1qx9t2l3pyny2spqpqlye8svce70nppwtaxwdrp4": "unknown wallet",
    "3QJRVfnJpzfNe1dr8hprCQrKJTnuRNwyrw": "unknown wallet",
    "bc1qtw30nantkrh7y5ue73gm4mmy0zezfqxug3psr94sd967qwg7f76scfmr9p": "wallet: 74625152",
    "17rm2dvb439dZqyMe2d4D6AQJSgg6yeNRn": "unknown wallet",
    "3H5JTt42K7RmZtromfTSefcMEFMMe18pMD": "Poloniex-coldwallet",
    "1PeizMg76Cf96nUQrYg8xuoZWLQozU5zGW": "unknown wallet",
    "bc1qqnt4td9a8xqrqtswvf6n27x0p8n948l2fgye3r6f3yk2d9838scs77ptr3": "wallet: 67449162",
    "38FkZJ32qaNTieBFUVHqQS1LQAZK8VFKkx": "unknown wallet",
    "3DVJfEsDTPkGDvqPCLC41X85L1B1DQWDyh": "OKEX-coldwallet",
    "35ULMyVnFoYaPaMxwHTRmaGdABpAThM4QR": "wallet: 67449162",
    "34MSicAL7qVGkevFPLwyc9KohGzoUSnu3Q": "unknown wallet",
    "1GR9qNz7zgtaW5HwwVpEJWMnGWhsbsieCG": "unknown wallet",
    "16S67V8PRG5sUh13Rgsj1AKVnpJYhHz4rN": "unknown wallet",
    "39gUvGynQ7Re3i15G3J2gp9DEB9LnLFPMN": "unknown wallet",
    "3ETUmNhL2JuCFFVNSpk8Bqx2eorxyP9FVh": "OKEX-coldwallet",
    "1KUr81aewyTFUfnq4ZrpePZqXixd59ToNn": "unknown wallet",
    "3BMEXxSMT2b2kvsnC4Q35d2kKJZ4u9bSLh": "unknown wallet",
    "3BMEXqGpG4FxBA1KWhRFufXfSTRgzfDBhJ": "BITMEX-coldwallet",
    "3EMVdMehEq5SFipQ5UfbsfMsH223sSz9A9": "unknown wallet",
    "1BZaYtmXka1y3Byi2yvXCDG92Tjz7ecwYj": "unknown wallet",
    "19iqYbeATe4RxghQZJnYVFU4mjUUu76EA6": "wallet: 62084963",
    "19G5kkYvjawZiYKhFeh8WmfBN31pdP94Jr": "unknown wallet",
    "35pgGeez3ou6ofrpjt8T7bvC9t6RrUK4p6": "wallet: 69400086",
    "1F34duy2eeMz5mSrvFepVzy7Y1rBsnAyWC": "unknown wallet",
    "bc1qhd0r5kh3u9mhac7de58qd2rdfx4kkv84kpx302": "unknown wallet",
    "3KTQYXvjteNoMECi62JYuqXobYQpcHjoVs": "Kraken-wallet",
    "3GQt3CF2w654acBveUh9DbdbXkTYovrfKg": "wallet: 68880850",
    "1f1miYFQWTzdLiCBxtHHnNiW7WAWPUccr": "unknown wallet",
    "3E5B5QbDjUL471PEed9vZDwCSck9btBLkD": "unknown wallet",
    "1BAFWQhH9pNkz3mZDQ1tWrtKkSHVCkc3fV": "unknown wallet",
    "14YK4mzJGo5NKkNnmVJeuEAQftLt795Gec": "unknown wallet",
    "1Ki3WTEEqTLPNsN5cGTsMkL2sJ4m5mdCXT": "unknown wallet",
    "1KbrSKrT3GeEruTuuYYUSQ35JwKbrAWJYm": "unknown wallet",
    "1P1iThxBH542Gmk1kZNXyji4E4iwpvSbrt": "unknown wallet",
    "12tLs9c9RsALt4ockxa1hB4iTCTSmxj2me": "unknown wallet",
    "1ucXXZQSEf4zny2HRwAQKtVpkLPTUKRtt": "unknown wallet",
    "1CPaziTqeEixPoSFtJxu74uDGbpEAotZom": "unknown wallet",
    "1LfV1tSt3KNyHpFJnAzrqsLFdeD2EvU1MK": "wallet: 33664448",
    "1PN1xjngm9jhY9duuR8af7CXmK3QVcsixJ": "unknown wallet",
    "3DwVjwVeJa9Z5Pu15WHNfKcDxY5tFUGfdx": "OKEX-coldwallet",
    "1LbUMzM7tmyVJCpzBJTi5ZVmRb2Vn8mwVH": "unknown wallet",
    "1AMDVupuTEeTSnKi6LoSFBqikQybufZsv1": "unknown wallet",
    "1DTmjcZo3MMH9MscHizTLjrUxnvwvSLdf7": "unknown wallet",
    "1JpAvQxbxurhU8wfxszCtzFey4D6N8goJv": "unknown wallet",
    "1EU2pMence1UfifCco2UHJCdoqorAtpT7": "unknown wallet",
    "1AFNceZVB2MshqU5AEoxg14R7LrUx6Un6C": "unknown wallet",
    "1BxgwUXszgVMrs9ZSfdcGLqne2vMYaW8jf": "unknown wallet",
    "3265tcUcp8dBhBBwp4rKN3iyUptuHkzMq7": "unknown wallet",
    "1Kd6zLb9iAjcrgq8HzWnoWNVLYYWjp3swA": "Kraken.com",
    "bc1qajh7jfy44sswutqlwj2tz9wcejpxrgflc8penw": "unknown wallet",
    "1P9fAFAsSLRmMu2P7wZ5CXDPRfLSWTy9N8": "unknown wallet",
    "1HLvaTs3zR3oev9ya7Pzp3GB9Gqfg6XYJT": "unknown wallet",
    "3QB2qhnj5Xxwhh3GKcfwQDSkL91BCCn5cp": "unknown wallet",
    "bc1qh4cpaydaqlzez8ekkasm3ygj4us7gwxsghh047": "unknown wallet",
    "17CzhFvGwH6TT46JtzhnhMpTw4mHYpEGCR": "Kraken.com",
    "bc1q78wmm8xnhveklsparpeq6drlg9wlq4lyahkqfp": "unknown wallet",
    "1Cr7EjvS8C7gfarREHCvFhd9gT3r46pfLb": "unknown wallet",
    "1J1F3U7gHrCjsEsRimDJ3oYBiV24wA8FuV": "F2Pool",
    "167ZWTT8n6s4ya8cGjqNNQjDwDGY31vmHg": "unknown wallet",
}
rich_addrs = list(rich_addrs_table.keys())

block_values = {}

if os.path.exists(pickle_file):
    with open(pickle_file, "rb") as f:
        block_values = pickle.load(f)

last_block = rpc_connection.getblockcount()


def total_value(current_block):
    value = 0
    for i in range(BLOCK_OFFSET - 1):
        try:
            value += block_values[current_block - i]
        except:
            pass
    return round(value, 4)


last_time = int(time.time() - 14400)
for i in range(BLOCK_OFFSET, -1, -1):
    block_number = last_block - i
    # ブロック情報を取得
    blhash = rpc_connection.getblockhash(block_number)
    blinfo = rpc_connection.getblock(blhash)
    # ブロック生成時間を計算
    current_time = blinfo["time"]
    timestamp = datetime.fromtimestamp(current_time).isoformat()
    block_time = current_time - last_time
    last_time = current_time
    if block_values.get(block_number) is not None:
        print(
            f"[{timestamp}] [{block_number}] value: {block_values[block_number]}[BTC], total: {total_value(last_block)}[BTC], block_time: {block_time}[sec]"
        )
        continue
    block_values[block_number] = 0
    # トランザクション内のBTC数を集計
    for txid in blinfo["tx"]:
        transaction = rpc_connection.decoderawtransaction(rpc_connection.getrawtransaction(txid))
        # 送信元のトランザクションを参照する
        for vin in transaction["vin"]:
            if not "txid" in vin:
                break
            in_txid = vin["txid"]
            in_no = vin["vout"]
            vout = rpc_connection.decoderawtransaction(rpc_connection.getrawtransaction(in_txid))["vout"][in_no]
            # 送信元アドレスと金額
            addresses = vout["scriptPubKey"].get("addresses", [])
            value = vout["value"]
            for addr in rich_addrs:
                if addr in addresses:
                    print(f"[{timestamp}] [{block_number}] tx:[{txid}] {rich_addrs_table.get(addr)}: -{value}BTC")
                    block_values[block_number] -= value
        # 送信先のアドレスと金額
        for vout in transaction["vout"]:
            addresses = vout["scriptPubKey"].get("addresses", [])
            value = vout["value"]
            for addr in rich_addrs:
                if addr in addresses:
                    print(f"[{timestamp}] [{block_number}] tx:[{txid}] {rich_addrs_table.get(addr)}: +{value}BTC")
                    block_values[block_number] += value

    with open(pickle_file, "wb") as f:
        pickle.dump(block_values, f)
    print(
        f"[{timestamp}] [{block_number}] value: {block_values[block_number]}[BTC], total: {total_value(last_block)}[BTC], block_time: {block_time}[sec]"
    )

while True:
    blockcount = rpc_connection.getblockcount()
    if last_block < blockcount:
        last_block = blockcount
        block_number = last_block
        # ブロック情報を取得
        blhash = rpc_connection.getblockhash(block_number)
        blinfo = rpc_connection.getblock(blhash)
        # ブロック生成時間を計算
        current_time = blinfo["time"]
        timestamp = datetime.fromtimestamp(current_time).isoformat()
        block_time = current_time - last_time
        last_time = current_time
        if block_values.get(block_number) is not None:
            print(
                f"[{timestamp}] [{block_number}] value: {block_values[block_number]}[BTC], total: {total_value(last_block)}[BTC], block_time: {block_time}[sec]"
            )
            continue
        block_values[block_number] = 0
        # トランザクション内のBTC数を集計
        for txid in blinfo["tx"]:
            transaction = rpc_connection.decoderawtransaction(rpc_connection.getrawtransaction(txid))
            # 送信元のトランザクションを参照する
            for vin in transaction["vin"]:
                if not "txid" in vin:
                    break
                in_txid = vin["txid"]
                in_no = vin["vout"]
                vout = rpc_connection.decoderawtransaction(rpc_connection.getrawtransaction(in_txid))["vout"][in_no]
                # 送信元アドレスと金額
                addresses = vout["scriptPubKey"].get("addresses", [])
                value = vout["value"]
                for addr in rich_addrs:
                    if addr in addresses:
                        print(f"[{timestamp}] [{block_number}] tx:[{txid}] {rich_addrs_table.get(addr)}: -{value}BTC")
                        block_values[block_number] -= value
            # 送信先のアドレスと金額
            for vout in transaction["vout"]:
                addresses = vout["scriptPubKey"].get("addresses", [])
                value = vout["value"]
                for addr in rich_addrs:
                    if addr in addresses:
                        print(f"[{timestamp}] [{block_number}] tx:[{txid}] {rich_addrs_table.get(addr)}: +{value}BTC")
                        block_values[block_number] += value

        with open(pickle_file, "wb") as f:
            pickle.dump(block_values, f)
        print(
            f"[{timestamp}] [{block_number}] value: {block_values[block_number]}[BTC], total: {total_value(last_block)}[BTC], block_time: {block_time}[sec]"
        )  # influxdbに書き込み
        client = InfluxDBClient(host="influxdb", port=8086, database="bots")
        data = [
            {"measurement": f"bitcoin", "fields": {"total_value": total_value(last_block), "block_time": block_time,},}
        ]
        client.write_points(data)
    time.sleep(10)
