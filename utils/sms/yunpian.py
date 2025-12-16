from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient
from typing import Dict, List
import os
from dotenv import load_dotenv

# 加载 .env（只在应用启动时调用一次）
load_dotenv()


class SmsRecallSender:
    def __init__(self) -> None:
        """初始化云片客户端，使用环境变量中的 API KEY。"""
        apikey = os.getenv("YUNPIAN_API_KEY")
        if not apikey:
            # 不直接抛异常，避免应用启动失败；发送时再报错更友好
            self.client = None
        else:
            self.client = YunpianClient(apikey)
    
    def send_recall_message(self, recall: Dict) -> Dict:
        """发送单条召回短信。"""
        if self.client is None:
            return {"status": "error", "message": "短信服务未配置：缺少 YUNPIAN_API_KEY"}

        mobile = recall.get("phone") or recall.get("contact")
        text = recall.get("message") or ""
        if not mobile or not text:
            return {"status": "error", "message": "缺少手机号或短信内容"}

        param = {YC.MOBILE: mobile, YC.TEXT: text}
        return self.client.sms().single_send(param)
    
    def send_recall_messages(self, recalls: List[Dict]) -> Dict:
        """
        批量发送召回短信。
        模板 ID 从环境变量 `YUNPIAN_TPL_ID` 读取，未配置时返回错误。
        """
        if self.client is None:
            return {"status": "error", "message": "短信服务未配置：缺少 YUNPIAN_API_KEY"}

        if not recalls:
            return {"status": "error", "message": "没有数据可发送"}

        tpl_id = os.getenv("YUNPIAN_TPL_ID")
        if not tpl_id:
            return {"status": "error", "message": "短信模板未配置：缺少 YUNPIAN_TPL_ID"}

        mobile_list: List[str] = []
        tpl_value_list: List[Dict] = []

        for recall in recalls:
            mobile = recall.get("contact") or recall.get("phone")
            if not mobile:
                continue

            mobile_list.append(mobile)
            tpl_value = {
                "username": recall.get("user_name") or recall.get("username") or "",
                "product": recall.get("product") or "",
                "coupon": str(recall.get("coupon", "")),
                "url": recall.get("url", ""),
            }
            tpl_value_list.append(tpl_value)

        if not mobile_list:
            return {"status": "error", "message": "未找到有效手机号"}

        param = {
            YC.MOBILE: ",".join(mobile_list),
            YC.TPL_ID: tpl_id,
            YC.TPL_VALUE: tpl_value_list,
        }
        return self.client.sms().tpl_batch_send(param)