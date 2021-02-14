#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
import sys
import threading
from datetime import datetime
from time import sleep
import numpy as np
import liquidtap
from logging import getLogger, config
import pandas as pd

class PriceLadders:
  # 初期処理
  def __init__(self):
    self.logger = getLogger(__name__)
    self.logger.info('start.')

  # price_ladders_cash_btcjpy_buyコールバック
  def update_callback_buy(self, data):
    self.logger.debug('update_callback_buy start.')
    global buyOriginData
    buyOriginData = data
    self.logger.debug('update_callback_buy end.')

  # price_ladders_cash_btcjpy_sellコールバック
  def update_callback_sell(self, data):
    self.logger.debug('update_callback_sell start.')
    global sellOriginData
    sellOriginData = data
    self.logger.debug('update_callback_sell end.')

  # pusher:connection_establishedコールバック
  def on_connect(self, data):
    self.logger.debug('on_connect start.')
    # コールバック設定
    tap_price.pusher.subscribe('price_ladders_cash_btcjpy_buy').bind('updated', self.update_callback_buy)
    tap_price.pusher.subscribe('price_ladders_cash_btcjpy_sell').bind('updated', self.update_callback_sell)
    self.logger.debug('on_connect end.')

  # liquidtap接続
  def set_liquidtap_price(self):
    self.logger.debug('set_liquidtap_price start.')
    global tap_price
    tap_price = liquidtap.Client()
    tap_price.pusher.connection.bind('pusher:connection_established', self.on_connect)
    tap_price.pusher.connect()
    self.logger.debug('set_liquidtap_price end.')

  # Priceデータ出力
  def print_price(self):
    # BUY
    buy_data = buyOriginData.split(',')
    buy_list = list(map(float, [s.translate(str.maketrans({'[':None, ']':None, '"':None})) for s in buy_data]))
    # SELL
    sell_data = sellOriginData.split(',')
    sell_list = list(map(float, [s.translate(str.maketrans({'[':None, ']':None, '"':None})) for s in sell_data]))
    # フォーマット変換
    df = pd.DataFrame({ 'buyPrice':buy_list[0::2],
                        'buySize':buy_list[1::2],
                        'sellPrice':sell_list[0::2],
                        'sellSize':sell_list[1::2]})
    # 累積和を列に追加
    df['buyCum'] = df['buySize'].cumsum()
    df['sellCum'] = df['sellSize'].cumsum()
    # ログ出力
    self.logger.info('\n{}'.format(df[['buyPrice','buySize','buyCum','sellPrice','sellSize','sellCum']].head(15)))

# 定期的に実行する処理
def interval_task():
    price.print_price()

# メイン
if __name__ == '__main__':
  # ログ設定
  config.fileConfig('./config/logging.conf')
  logger = getLogger(__name__)
  logger.info('start.')
  # 初期化
  price = PriceLadders()
  price.set_liquidtap_price()
  # 基準時刻を作る
  base_timing = datetime.now()
  interval_sec = 1
  # 無限ループ
  while True:
    try:
      # 基準時刻と現在時刻の剰余を元に、次の実行までの時間を計算する
      current_timing = datetime.now()
      elapsed_sec = (current_timing - base_timing).total_seconds()
      sleep_sec = interval_sec - (elapsed_sec % interval_sec)
      # 次の実行までsleep
      sleep(max(sleep_sec, 0))
      # スレッド実行
      t = threading.Thread(target=interval_task)
      t.start()
    # キーボード中断
    except KeyboardInterrupt:
      logger.info("Ctrl+Cで停止しました")
      break
    # その他のエクセプション
    except:
      pass
  logger.info('end.')
