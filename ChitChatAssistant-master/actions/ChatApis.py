# 访问图灵机器人openapi
# -*- coding: utf-8 -*-
"""
    ChatApis.py
    ~~~~~~~~~

     使用 requests 方式调用 OpenAI GPT-3.5 Chat API（兼容 Python 3.6）

"""
import requests
import json

# 设置 OpenAI API Key 和代理地址
API_KEY = '*****************************************'
API_URL = '*****************************************'

def get_response(msg):
    """
        调用 OpenAI GPT-3.5 接口获取对话回复（兼容 Python 3.6）

        :param msg 用户输入的文本消息
        :return string or None
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_KEY
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "你是一个友好、健谈的智能机器人"},
            {"role": "user", "content": msg}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("请求失败：", e)
        return None








