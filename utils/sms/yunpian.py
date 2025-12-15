from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient
from typing import Dict

class SmsRecallSender:
    def __init__(self, apikey):
        self.client = YunpianClient(apikey)
    
    def send_recall_message(self, recall) -> Dict:
        """发送召回消息"""
        param = {YC.MOBILE:recall["phone"],YC.TEXT:recall["message"]}
        # 获取返回结果, 返回码:r.code(),返回码描述:r.msg(),API结果:r.data(),其他说明:r.detail(),调用异常:r.exception()
        # 短信:clnt.sms() 账户:clnt.user() 签名:clnt.sign() 模版:clnt.tpl() 语音:clnt.voice() 流量:clnt.flow()
        return self.client.sms().single_send(param)
    
    def send_recall_messages(self, recalls) -> Dict:
        # 1. 准备批量发送数据
        # 模板ID（需要在云片后台创建并审核通过）
        # 例如模板内容：您的验证码是#code#，请在#time#分钟内使用
        tpl_id = 1234567
        
        # 2. 手机号列表
        mobile_list = []
        
        # 3. 对应的模板变量列表（长度必须与mobile_list一致）
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
        # 4. 批量发送短信
        param = {YC.MOBILE: ",".join(mobile_list),
                 YC.TPL_ID: tpl_id,
                 YC.TPL_VALUE: tpl_value_list}
        return self.client.sms().tpl_batch_send(param)