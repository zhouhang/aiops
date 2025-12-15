from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from services.dao.base_dao import BaseDAO
from services.dao.query_builder import QueryBuilder
import logging

logger = logging.getLogger(__name__)

class OrderDAO(BaseDAO):
    """订单数据访问对象"""
    
    def __init__(self):
        super().__init__("t_order")
    
    def create_order(self, order_data: Dict[str, Any]) -> int:
        """创建订单"""
        sql, params = QueryBuilder.build_insert_query(self.table_name, order_data)
        
        try:
            affected_rows = self.execute_update(sql, tuple(params))
            return affected_rows
        except Exception as e:
            logger.error(f"创建订单失败: {str(e)}")
            raise
    
    def batch_create_orders(self, orders_data: List[Dict[str, Any]]) -> int:
        """批量创建订单"""
        if not orders_data:
            return 0
        
        sql, params = QueryBuilder.build_batch_insert_query(self.table_name, orders_data)
        
        try:
            affected_rows = self.execute_update(sql, tuple(params))
            return affected_rows
        except Exception as e:
            logger.error(f"批量创建订单失败: {str(e)}")
            raise
    
    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        """根据ID获取订单"""
        conditions = {"id": order_id}
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            conditions=conditions
        )
        
        try:
            results = self.execute_query(sql, tuple(params))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"获取订单失败: {str(e)}")
            return None
    
    def get_order_by_merchant_order_id(self, merchant_id: int, merchant_order_id: str) -> Optional[Dict]:
        """根据商家ID和商家订单号获取订单"""
        conditions = {
            "merchant_id": merchant_id,
            "order_id": merchant_order_id
        }
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            conditions=conditions
        )
        
        try:
            results = self.execute_query(sql, tuple(params))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"获取订单失败: {str(e)}")
            return None
    
    def update_order(self, order_id: int, update_data: Dict[str, Any]) -> int:
        """更新订单"""
        conditions = {"id": order_id}
        
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
            logger.error(f"更新订单失败: {str(e)}")
            raise
    
    def query_orders(self, 
                    conditions: Optional[Dict[str, Any]] = None,
                    fields: Optional[List[str]] = None,
                    order_by: Optional[List[str]] = None,
                    limit: Optional[int] = None,
                    offset: Optional[int] = None) -> List[Dict]:
        """查询订单列表"""
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
            logger.error(f"查询订单失败: {str(e)}")
            return []
    
    def query_orders_paginated(self,
                              conditions: Optional[Dict[str, Any]] = None,
                              fields: Optional[List[str]] = None,
                              order_by: Optional[List[str]] = None,
                              page: int = 1,
                              page_size: int = 20) -> Dict:
        """分页查询订单"""
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
            logger.error(f"分页查询订单失败: {str(e)}")
            return {"data": [], "pagination": {}}
        finally:
            conn.close()
    
    def get_user_orders(self, 
                       merchant_id: int,
                       user_id: str,
                       limit: int = 50) -> List[Dict]:
        """获取用户的订单历史"""
        conditions = {
            "merchant_id": merchant_id,
            "user_id": user_id
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
            logger.error(f"获取用户订单失败: {str(e)}")
            return []
    
    def get_inactive_users(self,
                          merchant_id: int,
                          inactive_days: int = 30,
                          limit: int = 100) -> List[Dict]:
        """获取不活跃用户（超过指定天数未下单）"""
        # 计算截止日期
        cutoff_date = (datetime.now() - timedelta(days=inactive_days)).strftime('%Y-%m-%d')
        
        sql = """
        SELECT 
            user_id,
            MAX(name) as user_name,
            MAX(contact) as contact,
            MAX(contact_type) as contact_type,
            MAX(create_time) as last_order_time,
            COUNT(*) as total_orders,
            SUM(amount) as total_amount,
            DATEDIFF(CURDATE(), MAX(create_time)) as inactive_days
        FROM t_order
        WHERE merchant_id = %s
        GROUP BY user_id
        HAVING MAX(create_time) < %s
        ORDER BY MAX(create_time) ASC
        LIMIT %s
        """
        
        try:
            return self.execute_query(sql, (merchant_id, cutoff_date, limit))
        except Exception as e:
            logger.error(f"获取不活跃用户失败: {str(e)}")
            return []
    
    def get_sales_stats(self,
                       merchant_id: int,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> Dict:
        """获取销售统计"""
        conditions = {"merchant_id": merchant_id}
        
        if start_date and end_date:
            conditions["create_time"] = {"$between": [start_date, end_date]}
        elif start_date:
            conditions["create_time"] = {"$gte": start_date}
        elif end_date:
            conditions["create_time"] = {"$lte": end_date}
        
        sql, params = QueryBuilder.build_select_query(
            self.table_name,
            fields=[
                "COUNT(*) as order_count",
                "COUNT(DISTINCT user_id) as user_count",
                "SUM(amount) as total_amount",
                "AVG(amount) as avg_amount",
                "MIN(amount) as min_amount",
                "MAX(amount) as max_amount",
                "MIN(create_time) as first_order_time",
                "MAX(create_time) as last_order_time"
            ],
            conditions=conditions,
            group_by=["merchant_id"]
        )
        
        try:
            results = self.execute_query(sql, tuple(params))
            return results[0] if results else {}
        except Exception as e:
            logger.error(f"获取销售统计失败: {str(e)}")
            return {}
    
    def get_daily_sales(self,
                       merchant_id: int,
                       start_date: str,
                       end_date: str) -> List[Dict]:
        """获取每日销售数据"""
        sql = """
        SELECT 
            DATE(create_time) as order_date,
            COUNT(*) as order_count,
            COUNT(DISTINCT user_id) as user_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM t_order
        WHERE merchant_id = %s 
            AND DATE(create_time) >= %s 
            AND DATE(create_time) <= %s
        GROUP BY DATE(create_time)
        ORDER BY order_date
        """
        
        try:
            return self.execute_query(sql, (merchant_id, start_date, end_date))
        except Exception as e:
            logger.error(f"获取每日销售数据失败: {str(e)}")
            return []
    
    def get_top_products(self,
                        merchant_id: int,
                        limit: int = 10,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> List[Dict]:
        """获取热销商品"""
        conditions = {"merchant_id": merchant_id}
        
        if start_date and end_date:
            conditions["create_time"] = {"$between": [start_date, end_date]}
        
        sql = """
        SELECT 
            product,
            product_type,
            COUNT(*) as sales_count,
            SUM(amount) as sales_amount,
            COUNT(DISTINCT user_id) as user_count
        FROM t_order
        WHERE merchant_id = %s
        """
        
        params = [merchant_id]
        
        if start_date and end_date:
            sql += " AND create_time BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        sql += """
        GROUP BY product, product_type
        ORDER BY sales_count DESC, sales_amount DESC
        LIMIT %s
        """
        params.append(limit)
        
        try:
            return self.execute_query(sql, tuple(params))
        except Exception as e:
            logger.error(f"获取热销商品失败: {str(e)}")
            return []