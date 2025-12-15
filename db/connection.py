# db/connection.py
from dbutils.pooled_db import PooledDB
import pymysql
from db.config import DBConfig

# 创建连接池（全局单例）
pool = PooledDB(
    creator=pymysql,
    maxconnections=10,          # 最大连接数
    mincached=2,                # 初始化时缓存的连接数
    maxcached=5,                # 最大缓存连接数
    maxshared=0,                # 共享连接数（PyMySQL 不支持，设为0）
    blocking=True,              # 连接数满时是否等待
    host=DBConfig.HOST,
    port=DBConfig.PORT,
    user=DBConfig.USER,
    password=DBConfig.PASSWORD,
    database=DBConfig.DATABASE,
    charset=DBConfig.CHARSET,
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)

def get_db_connection():
    """从连接池获取连接"""
    return pool.connection()