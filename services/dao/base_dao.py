from typing import Dict, List, Any
from db.connection import get_db_connection
import logging
import pymysql

logger = logging.getLogger(__name__)

class BaseDAO:
    """基础数据访问对象"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def _get_connection(self):
        """获取数据库连接"""
        return get_db_connection()
    
    def execute_query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询语句"""
        conn = self._get_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params or ())
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询执行失败: {str(e)}")
            raise
        finally:
            conn.close()
    
    def execute_update(self, sql: str, params: tuple = None) -> int:
        """执行更新/插入/删除语句"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                affected_rows = cursor.rowcount
                conn.commit()
                return affected_rows
        except Exception as e:
            conn.rollback()
            logger.error(f"更新执行失败: {str(e)}")
            raise
        finally:
            conn.close()
    
    def execute_many(self, sql: str, params_list: List[tuple]) -> int:
        """批量执行语句"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.executemany(sql, params_list)
                affected_rows = cursor.rowcount
                conn.commit()
                return affected_rows
        except Exception as e:
            conn.rollback()
            logger.error(f"批量执行失败: {str(e)}")
            raise
        finally:
            conn.close()