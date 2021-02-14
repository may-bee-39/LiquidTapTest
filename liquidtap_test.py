#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from datetime import datetime
from time import sleep
from logging import getLogger, config
import orders
import price_ladders
import configparser

# ログ設定
config.fileConfig('./config/logging.conf')
logger = getLogger(__name__)

# 定期的に実行する処理
def interval_task():
    price.print_price()

# メイン
if __name__ == "__main__":
  logger.info('start.')
  # 設定値取得
  config_ini = configparser.ConfigParser()
  config_ini.read('config/config.ini', encoding='utf-8')
  read_default = config_ini['DEFAULT']
  token = read_default.get('token')
  secret = read_default.get('secret')
  # Price取得
  price = price_ladders.PriceLadders()
  price.set_liquidtap_price()
  # Order取得
  order = orders.Orders(token, secret)
  order.set_liquidtap_orders()
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
