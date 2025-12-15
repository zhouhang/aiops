from typing import Dict
from services.base_service import BaseService
from services.dao.order_dao import OrderDAO
import logging

logger = logging.getLogger(__name__)
orderDAO = OrderDAO()

class OrderService(BaseService):
    
    def __init__(self):
        super().__init__()

    def create_orders(self, orders: Dict) -> Dict:   
        if not orders:
            return {"status": "error", "message": "没有数据可存储"}
        return orderDAO.batch_create_orders(orders)