#!/usr/bin/env python
#_*_ coding:utf-8 _*_
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect
import redis
import logging
from logging.handlers import RotatingFileHandler

from ihome import utils
from config import Config_map

#数据库
db = SQLAlchemy()

#创始redis连接对象
redis_store = None

#为flask补充csrf防护机制
csrf = CSRFProtect()

####### 错误日志 #########
# logging.error("")   # 错误级别
# logging.warning("") #告警级别
# logging.info("")    #消息提示级别
# logging.debug("")   #调试级别

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) #调用debug级
# 创建日志记录器，指明日志保存路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/ihome.log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式、日志等级、输入日志信息的文件名行数、日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_log_handler)


# 工厂模式
def Create_app(Config_name):
    """
    创建flask的应用对象
    :param Config_name: str 配置模式的名字 {"develop", "product"}
    :return:
    """
    app = Flask(__name__)

    #根据配置模式的名字获取配置参数的类
    config_class = Config_map.get(Config_name)
    app.config.from_object(config_class)

    #使用app初始化DB
    db.init_app(app)

    #初始化redis工具
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT, password=config_class.REDIS_PASS)

    # 利用flask-session，将session数据保存到redis中
    Session(app)

    # 初始化
    csrf.init_app(app)

    #为flask添加自定义的转换器
    app.url_map.converters["re"] = utils.ReConverter

    #注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")

    return app