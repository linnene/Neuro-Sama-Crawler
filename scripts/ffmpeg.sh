#!/usr/bin/env bash

URL="https://cn-sdqd-cu-01-12.bilivideo.com/live-bvc/xxxxxxxx.flv?expires=..."

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

ffplay \
  -loglevel info \
  -fflags nobuffer \
  -user_agent "$UA" \
  -headers "Referer: https://live.bilibili.com/" \
  "https://cn-jssz-cm-02-08.bilivideo.com/live-bvc/794852/live_3546729368520811_28227759_2500.flv?expires=1766808895&pt=web&deadline=1766808895&len=0&oi=3402238448&platform=web&qn=250&trid=10000cf6f1ea7b11301907d322cf7c694f4f&uipk=100&uipv=100&nbs=1&bmt=1&uparams=cdn,deadline,len,oi,platform,qn,trid,uipk,uipv,nbs,bmt&cdn=cn-gotcha01&upsig=ff4512f25b79e305fcd904e9e8335ff0&site=fc38597b96366ca3454fdaed81ba099a&free_type=0&mid=0&sche=ban&sid=cn-jssz-cm-02-08&chash=1&sg=df&trace=4877&isp=other&rg=SouthWest&pv=Chongqing&p2p_type=1&hot_cdn=909769&origin_bitrate=6019&long_ab_flag=live_default_longitudinal&sk=7b9ca197a822eebb7933bf2a49b49d0f3c207a01b1e2d4f83086301be01c3a4a&strategy_version=latest&suffix=2500&pp=rtmp&strategy_ids=122&hdr_type=0&strategy_types=1&long_ab_id=45&media_type=0&long_ab_flag_value=test&info_source=cache&sl=2&source=puv3_onetier&deploy_env=prod&codec=0&score=1&vd=nc&zoneid_l=151404548&sid_l=stream_name_cold&src=puv3&order=1"