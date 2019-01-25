#!/usr/bin/env python
#_*_ coding:utf-8 _*_

from . import api
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