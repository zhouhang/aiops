from typing import Dict
from services.base_service import BaseService
from services.dao.recall_dao import RecallDAO
import logging
from datetime import datetime, timezone, timedelta
import uuid
from utils.sms.yunpian import SmsRecallSender

logger = logging.getLogger(__name__)
recallDAO = RecallDAO()
smsRecallSender = SmsRecallSender("123")

class RecallService(BaseService):

    def get_recall(self, token: str) -> Dict:
        if not token:
            return {"status": "error", "message": "Token不能为空"}
        return recallDAO.get_recall_by_token(token)

    def recall_click(self, token: str) -> int:
        if not token:
            return {"status": "error", "message": "召回ID不能为空"}
        # 更新召回记录为打开状态
        return recallDAO.mark_recall_clicked(token)

    def recall_claim(self, recall_id: int) -> int:
        if not recall_id:
            return {"status": "error", "message": "召回ID不能为空"}
        print(recall_id)
        # 更新召回记录为已认领状态
        return recallDAO.mark_recall_claimed(recall_id)

    def create_recalls(self, recalls: list[Dict]) -> int:
        if not recalls:
            return {"status": "error", "message": "没有数据可存储"}
        recall_records = []
        for recall in recalls:
            recall_record = {}
            recall_record["merchant_id"] = recall.get("merchant_id")
            recall_record["user_name"] = recall.get("user_name")
            recall_record["token"] = uuid.uuid4().hex
            recall_record["token_expired"] = datetime.now(timezone.utc) + timedelta(days=7)
            recall_record["product"] = recall.get("product")
            recall_record["product_type"] = recall.get("product_type")
            recall_record["contact"] = recall.get("contact")
            recall_record["contact_type"] = recall.get("contact_type")
            recall_records.append(recall_record)
        recallDAO.batch_create_recalls(recall_records)
        #发送短信
        return smsRecallSender.send_recall_messages(recall_records)