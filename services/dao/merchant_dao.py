from typing import Dict, List, Optional, Any
from services.dao.base_dao import BaseDAO
from services.dao.query_builder import QueryBuilder
import logging

logger = logging.getLogger(__name__)

class MerchantDAO(BaseDAO):
    """商家数据访问对象"""
    
    def __init__(self):
        super().__init__("t_merchant")
    
    def create_merchant(self, merchant_data: Dict[str, Any]) -> int:
        """创建商家"""
        sql, params = QueryBuilder.build_insert_query(self.table_name, merchant_data)
        
        try:
            affected_rows = self.execute_update(sql, tuple(params))
            return affected_rows
        except Exception as e:
            logger.error(f"创建商家失败: {str(e)}")
            raise
    
    def get_merchant_by_id(self, merchant_id: int) -> Optional[Dict]:
        """根据ID获取商家"""
        conditions = {"id": merchant_id}
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            conditions=conditions
        )
        
        try:
            results = self.execute_query(sql, tuple(params))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"获取商家失败: {str(e)}")
            return None
    
    def get_merchant_by_username(self, username: str) -> Optional[Dict]:
        """根据用户名获取商家"""
        conditions = {"username": username}
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            conditions=conditions
        )
        
        try:
            results = self.execute_query(sql, tuple(params))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"获取商家失败: {str(e)}")
            return None
    
    def update_merchant(self, merchant_id: int, update_data: Dict[str, Any]) -> int:
        """更新商家信息"""
        conditions = {"id": merchant_id}
        
        # 移除不能更新的字段
        update_data.pop('id', None)
        update_data.pop('create_time', None)
        
        sql, params = QueryBuilder.build_update_query(
            self.table_name,
            update_data,
            conditions
        )
        
        try:
            return self.execute_update(sql, tuple(params))
        except Exception as e:
            logger.error(f"更新商家失败: {str(e)}")
            raise
    
    def query_merchants(self, 
                       conditions: Optional[Dict[str, Any]] = None,
                       fields: Optional[List[str]] = None,
                       order_by: Optional[List[str]] = None,
                       limit: Optional[int] = None,
                       offset: Optional[int] = None) -> List[Dict]:
        """查询商家列表"""
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
            logger.error(f"查询商家失败: {str(e)}")
            return []
    
    def query_merchants_paginated(self,
                                 conditions: Optional[Dict[str, Any]] = None,
                                 fields: Optional[List[str]] = None,
                                 order_by: Optional[List[str]] = None,
                                 page: int = 1,
                                 page_size: int = 20) -> Dict:
        """分页查询商家"""
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
            logger.error(f"分页查询商家失败: {str(e)}")
            return {"data": [], "pagination": {}}
        finally:
            conn.close()
    
    def get_merchant_stats(self, merchant_id: Optional[int] = None) -> Dict:
        """获取商家统计信息"""
        conditions = {}
        if merchant_id:
            conditions["id"] = merchant_id
        
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            fields=[
                "COUNT(*) as total_merchants",
                "COUNT(DISTINCT industry) as industry_count",
                "MIN(create_time) as earliest_create",
                "MAX(create_time) as latest_create"
            ],
            conditions=conditions
        )
        
        try:
            results = self.execute_query(sql, tuple(params))
            return results[0] if results else {}
        except Exception as e:
            logger.error(f"获取商家统计失败: {str(e)}")
            return {}
    
    def delete_merchant(self, merchant_id: int) -> int:
        """删除商家（软删除）"""
        # 注意：实际项目中通常会做软删除
        update_data = {
            "is_deleted": 1,
            "update_time": "CURRENT_TIMESTAMP"
        }
        return self.update_merchant(merchant_id, update_data)