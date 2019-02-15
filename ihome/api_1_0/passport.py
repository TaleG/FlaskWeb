#!/usr/bin/env python
#_*_ coding:utf-8 _*_
import re
from flask import request, jsonify, current_app, session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from . import api
from ihome.utils.response_code import RET
from ihome import redis_store, db, constants
from ihome.models import User


@api.route("/users", methods=['POST'])
def register():
    """
    注册
    请求参数： 手机号   短信验证码   确认密码
    参数格式： json
    :return:
    """
    # 获取请求的json数据,返回字典
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')

    # 校验参数
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if not re.match(r"1[345678]\d{9}", mobile):
        # 表示格式不对
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg='两次输入密码不一致')

    # 从redis中取出短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码异常")


    # 判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")

    # 删除redis中的短信验证码，防止重复使用校验
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断用户填写短信验证码是否正确
    # if real_sms_code != sms_code:
    #     return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
    #
    # # 判断用户的手机号是否注册过
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    # else:
    #     if user is not None:
    #         # 表示手机号已存在
    #         return jsonify(errno=RET.DATAEXIST, errmgs="手机号已存在")

    # 保存用户的注册数据到数据库中，按数据库错误返回值来判断数据是否存在
    user = User(name=mobile, mobile=mobile)
    # user.generate_password_hash(password)
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后的回滚，回滚到commit()上一步，初始状态
        db.session.rollback()
        #表示手机号出现重复值，即手机号已注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmgs="手机号已存在")
    except Exception as e:
        current_app.logger.error(e)
        return  jsonify(errno=RET.DBERR, errmsg="查询数据库异常")
    # 保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")

@api.route("/sessions", methods=["POST"])
def login():
    """
    用户注册
    参数：手机号  密码
    格式：json
    :return:
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    # 校验参数
    # 参数完整的校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 手机号的格式
    if not re.match(r"1[345678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 判断错误次数是否超过限制，如果超过限制，则限制后续操作时间
    # redis记录："acess_num_"请求的IP: 次数
    user_ip = request.remote_addr   # 用户的IP地址

    try:
        access_nums = redis_store.get("access_nums_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多，请稍后重试")

    # 从数据库中根据手机号查询用户的数据进行对比验证
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    # 用数据库的密码与用户填写的密码进行对比验证
    if user is None or not user.check_password(password):
        # 如果验证失败，记录错误次数，反回信息
        try:
            redis_store.incr("access_nums_%s" % user_ip)
            redis_store.expire("access_nums_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    # 如果验证相同成功，保存登录状态，在session中
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id

    # 登录成功删除redis登录错误次数记录
    redis_store.delete("access_nums_%s" % user_ip)

    return jsonify(errno=RET.OK, errmsg="登录成功")

