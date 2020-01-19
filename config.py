#!/usr/bin/env python
#_*_ coding:utf-8 _*_
import redis

class Config(object):

    """配置信息"""

    DEBUG = True
    SECRET_KEY = "JIswqiji7JIiwqni*jkfdjU"

    #连接数据库
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3307/ihome_python04"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    #redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6380
    REDIS_PASS = '123456'

    #flask-session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)
    SESSION_USE_SIGNER = True #对cookie中的session进行隐藏
    PERMANENT_SESSION_LIFETIME = 604800 #设置session数据有效期，单位是秒

class DevelopmentConfig(Config):
    """开发者模式配置信息"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置信息"""
    pass

Config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
