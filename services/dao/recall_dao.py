from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from services.dao.base_dao import BaseDAO
from services.dao.query_builder import QueryBuilder
import logging

logger = logging.getLogger(__name__)

class RecallDAO(BaseDAO):
    """召回记录数据访问对象"""
    
    def __init__(self):
        super().__init__("t_recall")
    
    def create_recall(self, recall_data: Dict[str, Any]) -> int:
        """创建召回记录"""
        sql, params = QueryBuilder.build_insert_query(self.table_name, recall_data)
        
        try:
            affected_rows = self.execute_update(sql, tuple(params))
            return affected_rows
        except Exception as e:
            logger.error(f"创建召回记录失败: {str(e)}")
            raise
    
    def batch_create_recalls(self, recalls_data: List[Dict[str, Any]]) -> int:
        """批量创建召回记录"""
        if not recalls_data:
            return 0
        
        sql, params = QueryBuilder.build_batch_insert_query(self.table_name, recalls_data)
        
        try:
            affected_rows = self.execute_update(sql, tuple(params))
            return affected_rows
        except Exception as e:
            logger.error(f"批量创建召回记录失败: {str(e)}")
            raise
    
    def get_recall_by_id(self, recall_id: int) -> Optional[Dict]:
        """根据ID获取召回记录"""
        conditions = {"id": recall_id}
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            conditions=conditions
        )
        
        try:
            results = self.execute_query(sql, tuple(params))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"获取召回记录失败: {str(e)}")
            return None
    
    def get_recall_by_token(self, token: str) -> Optional[Dict]:
        """根据token获取召回记录"""
        conditions = {"token": token}
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            conditions=conditions
        )
        try:
            results = self.execute_query(sql, tuple(params))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"获取召回记录失败: {str(e)}")
            return None
    
    def update_recall(self, recall_id: int, update_data: Dict[str, Any]) -> int:
        """更新召回记录"""
        conditions = {"id": recall_id}
        
        # 移除不能更新的字段
        update_data.pop('id', None)
        update_data.pop('create_time', None)
        update_data.pop('token', None)  # token不能更新
        
        sql, params = QueryBuilder.build_update_query(
            self.table_name,
            update_data,
            conditions
        )
        
        try:
            return self.execute_update(sql, tuple(params))
        except Exception as e:
            logger.error(f"更新召回记录失败: {str(e)}")
            raise
    
    def mark_recall_clicked(self, token: str, click_time: Optional[datetime] = None) -> int:
        """标记召回记录为已点击"""
        update_data = {
            "click": 1,
            "click_time": click_time or datetime.now()
        }
        
        conditions = {"token": token}
        
        sql, params = QueryBuilder.build_update_query(
            self.table_name,
            update_data,
            conditions
        )
        
        try:
            return self.execute_update(sql, tuple(params))
        except Exception as e:
            logger.error(f"标记点击失败: {str(e)}")
            raise
    
    def mark_recall_claimed(self, token: str, claim_time: Optional[datetime] = None) -> int:
        """标记召回记录为已领取"""
        update_data = {
            "claim": 1,
            "claim_time": claim_time or datetime.now()
        }
        
        conditions = {"token": token}
        
        sql, params = QueryBuilder.build_update_query(
            self.table_name,
            update_data,
            conditions
        )

        try:
            return self.execute_update(sql, tuple(params))
        except Exception as e:
            logger.error(f"标记领取失败: {str(e)}")
            raise
    
    def mark_recall_writeoff(self, token: str, writeoff_time: Optional[datetime] = None) -> int:
        """标记召回记录为已核销"""
        update_data = {
            "writeoff": 1,
            "writeoff_time": writeoff_time or datetime.now()
        }
        
        conditions = {"token": token}
        
        sql, params = QueryBuilder.build_update_query(
            self.table_name,
            update_data,
            conditions
        )
        
        try:
            return self.execute_update(sql, tuple(params))
        except Exception as e:
            logger.error(f"标记核销失败: {str(e)}")
            raise
    
    def query_recalls(self, 
                     conditions: Optional[Dict[str, Any]] = None,
                     fields: Optional[List[str]] = None,
                     order_by: Optional[List[str]] = None,
                     limit: Optional[int] = None,
                     offset: Optional[int] = None) -> List[Dict]:
        """查询召回记录列表"""
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            fields=fields,
            conditions=conditions,
            order_by=order_by,
            limit=limit,
            offset=offset
        )
        
        try:
            return self.execute_query(sql, tuple(params))
        except Exception as e:
            logger.error(f"查询召回记录失败: {str(e)}")
            return []
    
    def query_recalls_paginated(self,
                               conditions: Optional[Dict[str, Any]] = None,
                               fields: Optional[List[str]] = None,
                               order_by: Optional[List[str]] = None,
                               page: int = 1,
                               page_size: int = 20) -> Dict:
        """分页查询召回记录"""
        data_sql, count_sql, data_params, count_params = QueryBuilder.build_paginated_query(
            self.table_name,
            fields=fields,
            conditions=conditions,
            order_by=order_by,
            page=page,
            page_size=page_size
        )
        
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cursor:
                # 查询数据
                cursor.execute(data_sql, tuple(data_params))
                data = cursor.fetchall()
                
                # 查询总数
                cursor.execute(count_sql, tuple(count_params))
                count_result = cursor.fetchone()
                total = count_result['total'] if count_result else 0
                
                return {
                    "data": data,
                    "pagination": {
                        "page": page,
                        "page_size": page_size,
                        "total": total,
                        "total_pages": (total + page_size - 1) // page_size
                    }
                }
        except Exception as e:
            logger.error(f"分页查询召回记录失败: {str(e)}")
            return {"data": [], "pagination": {}}
        finally:
            conn.close()
    
    def get_expired_recalls(self, before_date: Optional[datetime] = None) -> List[Dict]:
        """获取已过期的召回记录"""
        if not before_date:
            before_date = datetime.now()
        
        conditions = {
            "token_expired": {"$lt": before_date},
            "click": 0  # 只获取未点击的过期记录
        }
        
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            conditions=conditions,
            order_by=["token_expired ASC"],
            limit=1000
        )
        
        try:
            return self.execute_query(sql, tuple(params))
        except Exception as e:
            logger.error(f"获取过期召回记录失败: {str(e)}")
            return []
    
    def get_recall_stats(self,
                        merchant_id: Optional[int] = None,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> Dict:
        """获取召回统计"""
        conditions = {}
        
        if merchant_id:
            conditions["merchant_id"] = merchant_id
        
        if start_date and end_date:
            conditions["create_time"] = {"$between": [start_date, end_date]}
        elif start_date:
            conditions["create_time"] = {"$gte": start_date}
        elif end_date:
            conditions["create_time"] = {"$lte": end_date}
        
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            fields=[
                "COUNT(*) as total_recalls",
                "COUNT(CASE WHEN click = 1 THEN 1 END) as clicked_count",
                "COUNT(CASE WHEN claim = 1 THEN 1 END) as claimed_count",
                "COUNT(CASE WHEN writeoff = 1 THEN 1 END) as writeoff_count",
                "COUNT(CASE WHEN token_expired < NOW() THEN 1 END) as expired_count",
                "SUM(CASE WHEN click = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100 as click_rate",
                "SUM(CASE WHEN claim = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100 as claim_rate",
                "SUM(CASE WHEN writeoff = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100 as writeoff_rate",
                "MIN(create_time) as earliest_recall",
                "MAX(create_time) as latest_recall"
            ],
            conditions=conditions
        )
        
        try:
            results = self.execute_query(sql, tuple(params))
            stats = results[0] if results else {}
            
            # 格式化比率
            for key in ['click_rate', 'claim_rate', 'writeoff_rate']:
                if key in stats:
                    stats[key] = round(float(stats[key]), 2)
            
            return stats
        except Exception as e:
            logger.error(f"获取召回统计失败: {str(e)}")
            return {}
    
    def get_daily_recall_stats(self,
                              merchant_id: int,
                              start_date: str,
                              end_date: str) -> List[Dict]:
        """获取每日召回统计"""
        sql = """
        SELECT 
            DATE(create_time) as recall_date,
            COUNT(*) as total_recalls,
            COUNT(CASE WHEN click = 1 THEN 1 END) as clicked_count,
            COUNT(CASE WHEN claim = 1 THEN 1 END) as claimed_count,
            COUNT(CASE WHEN writeoff = 1 THEN 1 END) as writeoff_count,
            COUNT(CASE WHEN token_expired < NOW() THEN 1 END) as expired_count
        FROM t_recall
        WHERE merchant_id = %s 
            AND DATE(create_time) >= %s 
            AND DATE(create_time) <= %s
        GROUP BY DATE(create_time)
        ORDER BY recall_date
        """
        
        try:
            return self.execute_query(sql, (merchant_id, start_date, end_date))
        except Exception as e:
            logger.error(f"获取每日召回统计失败: {str(e)}")
            return []
    
    def get_user_recall_history(self,
                               merchant_id: int,
                               user_contact: str,
                               contact_type: str,
                               limit: int = 10) -> List[Dict]:
        """获取用户的召回历史"""
        conditions = {
            "merchant_id": merchant_id,
            "contact": user_contact,
            "contact_type": contact_type
        }
        
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            conditions=conditions,
            order_by=["create_time DESC"],
            limit=limit
        )
        
        try:
            return self.execute_query(sql, tuple(params))
        except Exception as e:
            logger.error(f"获取用户召回历史失败: {str(e)}")
            return []
    
    def cleanup_expired_recalls(self, before_date: Optional[datetime] = None) -> int:
        """清理过期召回记录（软删除或归档）"""
        if not before_date:
            before_date = datetime.now() - timedelta(days=30)  # 保留30天
        
        # 标记为已过期（软删除）
        update_data = {
            "status": "expired",
            "update_time": datetime.now()
        }
        
        conditions = {
            "token_expired": {"$lt": before_date},
            "click": 0
        }
        
        sql, params = QueryBuilder.build_update_query(
            self.table_name,
            update_data,
            conditions
        )
        
        try:
            return self.execute_update(sql, tuple(params))
        except Exception as e:
            logger.error(f"清理过期召回记录失败: {str(e)}")
            raise