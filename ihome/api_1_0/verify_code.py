#!/usr/bin/env python
#_*_ coding:utf-8 _*_

from flask import current_app, jsonify, make_response, request
import random

from . import api
from ihome import redis_store, constants, db
from ihome.utils.response_code import RET
from ihome.utils.captcha.captcha import captcha
from ihome.models import User

@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :params image_code_id: 图片验证码编号
    :return:
    """
    #业务逻辑处理
    #生成验证码图片
    #将验证码真实值与编号保存到redis中
    #返回图片
    #名字 真实文本 图片数据
    name, text, image_data = captcha.generate_captcha()
    # redis_store.set("image_code_%s" % image_code_id, text)
    # redis_store.expire("image_code_%s" %image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)
    #redis值：记录名、有效期、记录值
    try:
        redis_store.setex('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="save image code failed.")

    resp = make_response(image_data)
    resp.headers["Content-Type"] = 'image/jpg'
    return resp

# GET /api/v1.0/sms_codes/<mobile>?image_code=XXX&image_code_id=XXX
@api.route("/sms_codes/<re(r'1[345678]\d{9}'):mobile>")
def get_sms_code(mobile):
    """段信验证码"""
    # 获取参数
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')

    # 校验参数
    if not all([image_code_id, image_code]):
        # 表示参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 业务逻辑处理
    # 从Redis中取出真实的图片验证码
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="Redis数据库异常")

    # 判断图片验证码是否过期或没有
    if real_image_code is None:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")

    # 删除redis中的图片验证码，防止用户使用同一个图片验证码多次验证
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 图片验证码默认是Bytes类型（BytesIO），需要转格式为str类型。
    real_image_code_str = str(real_image_code, "utf-8")

    # 与用户填写的值对比，lower把两个值都转换成小写
    if real_image_code_str.lower() != image_code.lower():
        # 表示用户填写错误
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")

    # 判断对与这个手机号的操作，在60秒内有没有之前的记录，如果有，则认为用户操作频繁，不接受处理
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            # 表示只要不是在60秒内之前有过发送的记录
            return jsonify(errno=RET.REQERR, errmsg="请求过与频繁，请60秒后重试。")


    # 判断手机号是否存在
    # 从数据库中查mobile是否存在
    try:
        user =User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            # 表示手机号已存在
            return jsonify(errno=RET.DATAEXIST, errmgs="手机号已存在")

    # 如果手机号不存在发送短信，生成验证码。生成六位整数（%06d代表六位整数，0代表如果没有6位用0补全）
    sms_code = "%06d" % random.randint(0, 999999)
    # sms_code = '123456'

    # 保存真实的短信验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送给这个手机号的记录，防止用户在60s内再次触发发送短信操作
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存验证码异常")
    # 发送短信
    try:
        result = "0"
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")
    # 返回值
    if result == "0":
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")


