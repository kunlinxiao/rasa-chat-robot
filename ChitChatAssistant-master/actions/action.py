from typing import Dict, Text, Any, List, Union

from rasa_sdk import Tracker, Action
from rasa_sdk.events import UserUtteranceReverted, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from actions.WeatherApis import GaodeWeatherClient
from actions.ChatApis import get_response  # GPT-3.5 聊天回复


class NumberForm(FormAction):
    """用于处理号码相关查询的表单动作"""

    def name(self) -> Text:
        return "number_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        # 定义该表单必须填写的槽位（slots）
        return ["type", "number", "business"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        # 槽位与提取方式的映射关系
        return {
            "type": self.from_entity(entity="type", not_intent="chitchat"),
            "number": self.from_entity(entity="number", not_intent="chitchat"),
            "business": [
                self.from_entity(entity="business", intent=["inform", "request_number"]),
                self.from_entity(entity="business"),
            ],
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        # 所有必填槽位填写完成后执行的操作
        number_type = tracker.get_slot('type')
        number = tracker.get_slot('number')
        business = tracker.get_slot('business')

        if not business:
            dispatcher.utter_message(
                text=f"您要查询的{number_type}{number}所属人为张三，湖南长沙人，现在就职于地球村物业管理有限公司。"
            )
            return []

        dispatcher.utter_message(
            text=f"你要查询{number_type}为{number}的{business}为：balabalabalabalabala。"
        )
        return [SlotSet("business", None)]  # 查询后清除 business 槽位


# 初始化天气客户端（在文件顶部）
WEATHER_CLIENT = GaodeWeatherClient(api_key="5bad9766fc52948d56b8f20c22c9086f")
class WeatherForm(FormAction):
    """用于处理天气查询的表单动作"""

    def name(self) -> Text:
        return "weather_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["address"]  # 仅需要提供地址

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        address = tracker.get_slot('address')
        if not address:
            dispatcher.utter_message("未提供城市，无法查询天气。")
            return []

        msg = WEATHER_CLIENT.get_3day_forecast(address)
        dispatcher.utter_message(msg)
        return []


class ActionDefaultFallback(Action):
    """处理无法识别的用户输入（默认回退动作）"""

    def name(self) -> Text:
        return 'action_default_fallback'

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # 获取用户的最后一句话
        text = tracker.latest_message.get('text')

        # 使用 ChatGPT 3.5 接口尝试生成回复
        message = get_response(text)
        if message is not None:
            dispatcher.utter_message(message)
        else:
            dispatcher.utter_message("对不起，我没听懂您的意思。")

        # 回退到用户上一条输入前的状态
        return [UserUtteranceReverted()]


# 测试代码
if __name__ == "__main__":
    # 创建一个测试的 dispatcher
    dispatcher = CollectingDispatcher()
    # 创建一个测试的 tracker
    sender_id = "test_user"
    slots = {"type": "电话号码", "number": "1234567890", "address": "北京"}
    latest_message = {"text": "你好"}
    events = []
    paused = False
    followup_action = None
    active_form = None
    latest_action_name = None
    tracker = Tracker(
        sender_id, slots, latest_message, events, paused, followup_action, active_form, latest_action_name
    )
    # 创建一个测试的 domain
    domain = {}

    # 测试 NumberForm
    number_form = NumberForm()
    number_form.submit(dispatcher, tracker, domain)
    print(dispatcher.messages[-1])  # 打印最新消息

    # 测试 WeatherForm
    weather_form = WeatherForm()
    weather_form.submit(dispatcher, tracker, domain)
    print(dispatcher.messages[-1])  # 打印最新消息

    # 测试 ActionDefaultFallback
    fallback_action = ActionDefaultFallback()
    fallback_action.run(dispatcher, tracker, domain)
    print(dispatcher.messages[-1])  # 打印最新消息