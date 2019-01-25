#!/usr/bin/env python
#_*_ coding:utf-8 _*_

from flask import Blueprint, current_app

# 提供表态文件的蓝图
html = Blueprint("web_html", __name__)

@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    """提供html文件"""

    #如果html_file_name为空，表示访问的路径是/，请求的是主页。
    if not html_file_name:
        html_file_name = 'index.html'
    if html_file_name != 'favicon.ico':
        html_file_name = "html/" + html_file_name
    #flask提供的返回静态文件的方法
    return current_app.send_static_file(html_file_name)