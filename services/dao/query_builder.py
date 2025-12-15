from typing import Dict, List, Optional, Tuple, Any

class QueryBuilder:
    """SQL查询构建器"""
    
    @staticmethod
    def build_select_query(table: str, 
                          fields: Optional[List[str]] = None,
                          conditions: Optional[Dict[str, Any]] = None,
                          order_by: Optional[List[str]] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None,
                          group_by: Optional[List[str]] = None) -> Tuple[str, List[Any]]:
        """
        构建SELECT查询语句
        
        Args:
            table: 表名
            fields: 查询字段列表，None表示所有字段
            conditions: 查询条件字典
            order_by: 排序字段列表
            limit: 限制条数
            offset: 偏移量
            group_by: 分组字段
            
        Returns:
            (sql语句, 参数列表)
        """
        # 构建SELECT部分
        if not fields:
            select_clause = "SELECT *"
        else:
            select_clause = f"SELECT {', '.join(fields)}"
        
        # 构建FROM部分
        from_clause = f"FROM {table}"
        
        # 构建WHERE部分
        where_clause, where_params = QueryBuilder._build_where_clause(conditions)
        
        # 构建GROUP BY部分
        group_clause = ""
        if group_by:
            group_clause = f"GROUP BY {', '.join(group_by)}"
        
        # 构建ORDER BY部分
        order_clause = ""
        if order_by:
            order_clause = f"ORDER BY {', '.join(order_by)}"
        
        # 构建LIMIT/OFFSET部分
        limit_clause = ""
        params = where_params
        
        if limit is not None:
            limit_clause = "LIMIT %s"
            params.append(limit)
            
            if offset is not None:
                limit_clause += " OFFSET %s"
                params.append(offset)
        
        # 组合SQL语句
        sql_parts = [select_clause, from_clause, where_clause, group_clause, order_clause, limit_clause]
        sql = " ".join(filter(None, sql_parts))
        
        return sql, params
    
    @staticmethod
    def _build_where_clause(conditions: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Any]]:
        """构建WHERE子句"""
        if not conditions:
            return "", []
        
        where_conditions = []
        params = []
        
        for field, value in conditions.items():
            if value is None:
                continue
                
            # 处理特殊操作符
            if isinstance(value, dict):
                for op, op_value in value.items():
                    if op == "$gt":
                        where_conditions.append(f"{field} > %s")
                        params.append(op_value)
                    elif op == "$gte":
                        where_conditions.append(f"{field} >= %s")
                        params.append(op_value)
                    elif op == "$lt":
                        where_conditions.append(f"{field} < %s")
                        params.append(op_value)
                    elif op == "$lte":
                        where_conditions.append(f"{field} <= %s")
                        params.append(op_value)
                    elif op == "$ne":
                        where_conditions.append(f"{field} != %s")
                        params.append(op_value)
                    elif op == "$like":
                        where_conditions.append(f"{field} LIKE %s")
                        params.append(f"%{op_value}%")
                    elif op == "$in":
                        if not op_value:
                            continue
                        placeholders = ', '.join(['%s'] * len(op_value))
                        where_conditions.append(f"{field} IN ({placeholders})")
                        params.extend(op_value)
                    elif op == "$between":
                        if len(op_value) == 2:
                            where_conditions.append(f"{field} BETWEEN %s AND %s")
                            params.extend(op_value)
            elif isinstance(value, list):
                # IN 查询
                if not value:
                    continue
                placeholders = ', '.join(['%s'] * len(value))
                where_conditions.append(f"{field} IN ({placeholders})")
                params.extend(value)
            elif isinstance(value, str) and '%' in value:
                # LIKE 查询
                where_conditions.append(f"{field} LIKE %s")
                params.append(value)
            elif isinstance(value, bool):
                # 布尔值转换
                where_conditions.append(f"{field} = %s")
                params.append(1 if value else 0)
            else:
                # 普通等值查询
                where_conditions.append(f"{field} = %s")
                params.append(value)
        
        if where_conditions:
            return "WHERE " + " AND ".join(where_conditions), params
        else:
            return "", params
    
    @staticmethod
    def build_count_query(table: str, 
                         conditions: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Any]]:
        """
        构建COUNT查询语句
        """
        return QueryBuilder.build_select_query(
            table=table,
            fields=["COUNT(*) as total"],
            conditions=conditions,
            order_by=None,
            limit=None,
            offset=None
        )
    
    @staticmethod
    def build_paginated_query(table: str,
                             fields: Optional[List[str]] = None,
                             conditions: Optional[Dict[str, Any]] = None,
                             order_by: Optional[List[str]] = None,
                             page: int = 1,
                             page_size: int = 20) -> Tuple[str, str, List[Any], List[Any]]:
        """
        构建分页查询
        """
        # 数据查询
        data_sql, data_params = QueryBuilder.build_select_query(
            table=table,
            fields=fields,
            conditions=conditions,
            order_by=order_by,
            limit=page_size,
            offset=(page - 1) * page_size
        )
        
        # 计数查询
        count_sql, count_params = QueryBuilder.build_count_query(
            table=table,
            conditions=conditions
        )
        
        return data_sql, count_sql, data_params, count_params
    
    @staticmethod
    def build_insert_query(table: str, data: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        构建INSERT语句
        """
        columns = []
        values = []
        params = []
        
        for column, value in data.items():
            if value is not None:
                columns.append(column)
                values.append("%s")
                params.append(value)
        
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)})"
        return sql, params
    
    @staticmethod
    def build_batch_insert_query(table: str, data_list: List[Dict[str, Any]]) -> Tuple[str, List[Any]]:
        """
        构建批量INSERT语句
        """
        if not data_list:
            raise ValueError("数据列表不能为空")
        
        # 获取所有列
        columns = list(data_list[0].keys())
        
        # 构建值列表
        values_list = []
        params = []
        
        for data in data_list:
            row_values = []
            for column in columns:
                value = data.get(column)
                row_values.append("%s")
                params.append(value)
            values_list.append(f"({', '.join(row_values)})")
        
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES {', '.join(values_list)}"
        return sql, params
    
    @staticmethod
    def build_update_query(table: str, 
                          data: Dict[str, Any],
                          conditions: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Any]]:
        """
        构建UPDATE语句
        """
        set_clause = []
        params = []
        
        for column, value in data.items():
            if value is not None:
                set_clause.append(f"{column} = %s")
                params.append(value)
        
        if not set_clause:
            raise ValueError("更新数据不能为空")
        
        sql = f"UPDATE {table} SET {', '.join(set_clause)}"
        
        # 添加WHERE条件
        if conditions:
            where_clause, where_params = QueryBuilder._build_where_clause(conditions)
            if where_clause:
                sql += " " + where_clause
                params.extend(where_params)
        
        return sql, params