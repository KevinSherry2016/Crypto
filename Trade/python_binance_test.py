import time
import uuid
from decimal import Decimal as D
from binance.client import Client


ORDER_SYMBOL = "BTCUSDT"        # 查询持仓、挂单及下单的交易对。
API_KEY = "5TuntjtR4eKGj4BpWR4dmnFp2KCtnJVg3nrDDtLw57Aex9san6exRzu9fSqH3n7G"
API_SECRET = "CYMMn5JUfWeRgdxJzaXX6Fe4jQh4g1G51HvqYLfNnB2gbiwXxvbyWhnBBs1d9Fg9"
TEST_TRADING = False            # True 只提交一笔市价开仓单，成交后保留仓位。
CONFIRM_LIVE = False            # 实盘交易还需显式开启此项。
POSITION_SIDE = "LONG"          # LONG 开多，SHORT 开空；不自动平仓。
QUANTITY = "0.002"              # 每笔基础资产数量，不是 USDT 金额。


def run(client):
    before = time.time_ns() // 1_000_000
    server = client.futures_time()["serverTime"]
    client.timestamp_offset = server - (before + time.time_ns() // 1_000_000) // 2
    hedged = client.futures_get_position_mode()["dualSidePosition"]
    if type(hedged) is not bool:
        raise ValueError("持仓模式响应异常。")
    account = client.futures_account()
    print("余额/权益/可用余额：", account["totalWalletBalance"], account["totalMarginBalance"], account["availableBalance"])
    positions = client.futures_position_information(symbol=ORDER_SYMBOL)
    orders = client.futures_get_open_orders(symbol=ORDER_SYMBOL)
    algo = client.futures_get_open_algo_orders(symbol=ORDER_SYMBOL)
    print(f"\n{ORDER_SYMBOL} 持仓：", [p for p in positions if D(p["positionAmt"])])
    print(f"环境=实盘，双向持仓={hedged}，挂单={len(orders)}，条件单={len(algo)}")
    if not TEST_TRADING:
        print("查询完成，未下单。")
        return
    quantity = D(QUANTITY)
    if POSITION_SIDE not in ("LONG", "SHORT") or not quantity.is_finite() or quantity <= 0:
        raise ValueError("方向须为 LONG/SHORT，数量须为正有限数。")
    if orders or algo or any(D(p["positionAmt"]) for p in positions):
        raise ValueError("目标交易对已有仓位或挂单，请先人工检查。")
    # 数量精度、最低名义金额及保证金由交易所校验；只提交一次，不重试。
    client_id = "pb_" + uuid.uuid4().hex[:28]
    print("提交市价单，客户端订单 ID：", client_id, flush=True)
    submitted = client.futures_create_order(
        symbol=ORDER_SYMBOL, side="BUY" if POSITION_SIDE == "LONG" else "SELL",
        positionSide=POSITION_SIDE if hedged else "BOTH", type="MARKET",
        quantity=str(quantity), newClientOrderId=client_id, newOrderRespType="RESULT")
    print("订单：", client.futures_get_order(symbol=ORDER_SYMBOL, orderId=submitted["orderId"]))
    print("持仓：", client.futures_position_information(symbol=ORDER_SYMBOL))
    print("只提交了一笔开仓单，未自动平仓；请根据以上状态确认成交及仓位。")


def main():
    if TEST_TRADING and not CONFIRM_LIVE:
        raise ValueError("实盘交易需设置 CONFIRM_LIVE = True。")
    if not API_KEY.strip() or not API_SECRET.strip():
        raise ValueError("请在顶部填写对应环境的 API_KEY 和 API_SECRET。")
    client = Client(API_KEY.strip(), API_SECRET.strip(), ping=False,
                    requests_params={"timeout": 10})
    try:
        run(client)
    finally:
        client.close_connection()


if __name__ == "__main__":
    main()
