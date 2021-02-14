#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
from time import sleep
import liquidtap
from logging import getLogger, config
import configparser

class Orders:
  # 初期処理
  def __init__(self, token, secret):
    self.logger = getLogger(__name__)
    self.logger.info('start.')
    self.token = token
    self.secret = secret

  # ログ出力
  def log_print(self, callback, data):
    json_data = json.loads(data)
    self.logger.info("{}:\n{}\n".format(callback, json.dumps(json_data, indent=2)))

  # user_account_jpy_ordersコールバック
  def executions_callback(self, data):
    self.log_print("executions", data)

  # user_account_jpy_tradesコールバック
  def trades_callback(self, data):
    self.log_print("trades", data)

  # user_executions_cash_btcjpyコールバック
  def orders_callback(self, data):
    self.log_print("orders", data)

  # liquidtap接続
  def set_liquidtap_orders(self):
    global tap_orders
    tap_orders = liquidtap.Client(self.token, self.secret)
    self.logger.info('token:'+ self.token + ' secret:'+ self.secret)
    tap_orders.pusher.connect()
    # コールバック設定
    tap_orders.subscribe("user_account_jpy_orders").bind('updated', self.orders_callback)
    tap_orders.subscribe("user_account_jpy_trades").bind('updated', self.trades_callback)
    tap_orders.subscribe("user_executions_cash_btcjpy").bind('created', self.executions_callback)

# メイン
if __name__ == "__main__":
  # 設定値取得
  config_ini = configparser.ConfigParser()
  config_ini.read('config/config.ini', encoding='utf-8')
  read_default = config_ini['DEFAULT']
  token = read_default.get('token')
  secret = read_default.get('secret')

  # ログ設定
  config.fileConfig('./config/logging.conf')
  logger = getLogger(__name__)
  logger.info('start.')
  # 初期化
  orders = Orders(token, secret)
  orders.set_liquidtap_orders()
  # 無限ループ
  while True:
    try:
      sleep(1)
      # キーボード中断
    except KeyboardInterrupt:
      logger.info("Ctrl+Cで停止しました")
      break
    # その他のエクセプション
    except:
      pass
  logger.info('end.')
