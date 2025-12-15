# db/config.py
import os
from dotenv import load_dotenv
import pymysql

# 加载 .env（只在应用启动时调用一次）
load_dotenv()

class DBConfig:
    HOST = os.getenv("DB_HOST", "127.0.0.1")
    PORT = int(os.getenv("DB_PORT", "3306"))
    USER = os.getenv("DB_USER", "aiops")
    PASSWORD = os.getenv("DB_PASSWORD", "654321")
    DATABASE = os.getenv("DB_NAME", "aiops")
    CHARSET = os.getenv("CHARSET", "UTF8MB4")
    
    @classmethod
    def to_dict(cls):
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "user": cls.USER,
            "password": cls.PASSWORD,
            "database": cls.DATABASE,
            "charset": cls.CHARSET,
            "autocommit": True,
            "cursorclass": pymysql.cursors.DictCursor  # 默认返回字典
        }