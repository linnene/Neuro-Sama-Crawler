#!/usr/bin/env bash

URL="https://cn-sdqd-cu-01-12.bilivideo.com/live-bvc/xxxxxxxx.flv?expires=..."

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

ffplay \
  -loglevel info \
  -fflags nobuffer \
  -user_agent "$UA" \
  -headers "Referer: https://live.bilibili.com/" \
  "https://d1--cn-gotcha04.bilivideo.com/live-bvc/760455/live_3546729368520811_28227759_2500.flv?expires=1766661564&len=0&oi=3402238448&pt=web&qn=250&trid=10005fc3e0171ac71c55067e55893e694d0f&bmt=1&sigparams=cdn,expires,len,oi,pt,qn,trid,bmt&cdn=cn-gotcha04&sign=a4e69f838084cbe39d8c71166e8afa11&site=c7e26f04dcdc80bf633fd399f7aa1416&free_type=0&mid=0&sche=ban&trace=4&isp=other&rg=SouthWest&pv=Chongqing&hot_cdn=909449&long_ab_id=45&p2p_type=1&pp=rtmp&hdr_type=0&sl=2&suffix=2500&long_ab_flag=live_default_longitudinal&origin_bitrate=6023&strategy_types=1&strategy_ids=122&info_source=origin&source=puv3_onetier&deploy_env=prod&long_ab_flag_value=test&strategy_version=latest&codec=0&sk=3ff3d081192b939627f646d4ec98d0a9c63dfdadea5df190deff41967c05daf8&media_type=0&score=1&vd=bc&src=puv3&order=1"