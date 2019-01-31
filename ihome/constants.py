#!/usr/bin/env python
#_*_ coding:utf-8 _*_

# 设置图片验证码的redis有效期，单位:秒
IMAGE_CODE_REDIS_EXPIRES = 180

# 设置短信验证码的redis有效期，单位:秒
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的间隔， 单位：秒
SEND_SMS_CODE_INTERVAL = 60