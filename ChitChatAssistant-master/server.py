"""
    server.py
    ~~~~~~~~~

    web server，定义前端调用接口

    :date: 2020-02-14 14:36:00
    :author: by jiangdg
"""

from flask import Flask, jsonify
from flask import request
from flask import render_template
import os
import requests
import json
import logging

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def test():
    return"测试"

@app.route('/chat', methods=['GET'])
def chat_ui():
    return render_template('index.html')

@app.route('/ai', methods=['GET', 'POST'])
def webToBot():
    """
    前端调用接口
        路径：/ai
        请求方式：GET、POST
        请求参数：content
    :return: response rasa响应数据
    """
    content = request.values.get('content')
    if not content:
        return 'empty input'
    response = requestRasabotServer('jiangdg', content)

    if response.status_code != 200:
        return "Rasa 请求失败"

    try:
        # 取出 Rasa 回复的第一条 text
        result_json = response.json()
        if not result_json:
            return "Rasa 没有返回内容"
        return result_json[0].get("text", "无回复内容")
    except Exception as e:
        return f"解析出错: {str(e)}"


def requestRasabotServer(userid, content):
    """
        访问rasa服务
    :param userid: 用户id
    :param content: 自然语言文本
    :return:  Response 对象
    """
    payload = {'sender': userid, 'message': content}
    rasa_url = "http://127.0.0.1:5005/webhooks/rest/webhook"
    headers = {'Content-Type': 'application/json'}

    # rasa使用rest channel
    # https://rasa.com/docs/rasa/user-guide/connectors/your-own-website/#rest-channels
    # POST /webhooks/rest/webhook
    # rasaUrl = "http://{0}:{1}/webhooks/rest/webhook".format(botIp, botPort)
    try:
        response = requests.post(rasa_url, json=payload, headers=headers)
        return response
    except Exception as e:
        print(f"[ERROR] 请求 Rasa 出错: {e}")
        return None


if __name__ == '__main__':
    webIp = '127.0.0.1'
    webPort = '8088'

    print("##### webIp={}, webPort={}".format(webIp, webPort))
    # 初始化日志引擎
    fh = logging.FileHandler(encoding='utf-8', mode='a', filename='chitchat.log')
    logging.basicConfig(
        handlers=[fh],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
    )

    # 启动服务，开启多线程、debug模式
    # 浏览器访问http://127.0.0.1:8088/ai?content="你好"
    # http://127.0.0.1:8088/chat
    app.run(
        host=webIp,
        port=int(webPort),
        threaded=True,
        debug=True
    )
