from typing import Dict
from services.base_service import BaseService
from services.dao.merchant_dao import MerchantDAO
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
merchantDao = MerchantDAO()

class MerchantService(BaseService):

    def get_merchant_by_id(self, merchant_id: int) -> Dict:
        if not merchant_id:
            return {"status": "error", "message": "商户ID不能为空"}
        return merchantDao.get_merchant_by_id(merchant_id)
    
    def get_merchant_by_username(self, username: str) -> Dict:
        if not username:
            return None
        return merchantDao.get_merchant_by_username(username)

    def create_merchant(self, merchant_data: Dict) -> int:
        if not merchant_data:
            return {"status": "error", "message": "没有商户数据可存储"}
        merchant_data["created_at"] = datetime.now(timezone.utc)
        return merchantDao.create_merchant(merchant_data)

    def update_merchant(self, merchant_id: int, merchant_data: Dict) -> int:
        if not merchant_id or not merchant_data:
            return {"status": "error", "message": "商户ID或数据不能为空"}
        merchant_data["updated_at"] = datetime.now(timezone.utc)
        return merchantDao.update_merchant(merchant_id, merchant_data)