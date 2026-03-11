from dataclasses import dataclass


@dataclass
class MysqlConfig:
    """mysql配置"""
    
    host: str = "106.63.13.52"
    """Mysql 主机"""
    
    port: int = 25001
    """Mysql 端口"""
    
    user: str = "szzf"
    """用户名"""
    
    password: str = "jRzZHvnjRm1kJ9fRj5SL"
    """数据库密码"""
    
    database: str = "db_knowledge_kg"
    """数据库名"""