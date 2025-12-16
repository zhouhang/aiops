from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient
from typing import Dict
import os
from dotenv import load_dotenv

# 加载 .env（只在应用启动时调用一次）
load_dotenv()

class SmsRecallSender:
    def __init__(self):
        apikey = os.getenv("YUNPIAN_API_KEY")
        self.client = YunpianClient(apikey)
    
    def send_recall_message(self, recall) -> Dict:
        """发送召回消息"""
        param = {YC.MOBILE:recall["phone"],YC.TEXT:recall["message"]}
        # 获取返回结果, 返回码:r.code(),返回码描述:r.msg(),API结果:r.data(),其他说明:r.detail(),调用异常:r.exception()
        # 短信:clnt.sms() 账户:clnt.user() 签名:clnt.sign() 模版:clnt.tpl() 语音:clnt.voice() 流量:clnt.flow()
        return self.client.sms().single_send(param)
    
    def send_recall_messages(self, recalls: list[Dict], tpl_id: int) -> Dict:
        if not recalls or not tpl_id:
            return {"status": "error", "message": "没有数据或模板ID"}
        # 1. 手机号列表
        mobile_list = []
        
        # 2. 对应的模板变量列表（长度必须与mobile_list一致）
        tpl_value_list = [
            {"username": "1234", "product": "5", "coupon": "5", "url": "5"},     # 第一个手机号的变量
        ]
        tpl_value = {}
        """发送召回消息"""
        for recall in recalls:
            mobile_list.append(recall["contact"])
            tpl_value["username"] = recall["username"]
            tpl_value["product"] = recall["product"]
            tpl_value["coupon"] = recall["coupon"]
            tpl_value["url"] = recall["url"]
            tpl_value_list.append(tpl_value)
        # 3. 批量发送短信
        param = {YC.MOBILE: ",".join(mobile_list),
                 YC.TPL_ID: tpl_id,
                 YC.TPL_VALUE: tpl_value_list}
        return self.client.sms().tpl_batch_send(param)