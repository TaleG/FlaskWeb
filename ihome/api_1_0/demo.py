#!/usr/bin/env python
#_*_ coding:utf-8 _*_

from . import api
from flask import current_app
from ihome import models

@api.route('/index')
def hello_world():
    current_app.logger.error("error msg")
    current_app.logger.warning("error msg")
    current_app.logger.info("info mgs")
    current_app.logger.debug("debug mgs")
    return 'Hello World!'
