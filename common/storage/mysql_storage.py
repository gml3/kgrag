"""
MySQL 存储辅助

提供面向对象的 MySQL 存储与读取服务，将数据模型序列化为 DataFrame 写入或读出。
"""

import json
import logging
from dataclasses import asdict
from typing import List, Any

import pandas as pd
from sqlalchemy import create_engine

from common.config.models.mysql_config import MysqlConfig

logger = logging.getLogger(__name__)


class MysqlStorage:
    """MySQL 数据库存储和读取服务"""

    def __init__(self, config: MysqlConfig):
        """初始化存储连接引擎。
        
        Args:
            config: MySQL 配置对象
        """
        self.config = config
        db_url = f"mysql+pymysql://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}?charset=utf8mb4"
        self.engine = create_engine(db_url)

    def save(self, data: List[Any], table_name: str, if_exists: str = "append") -> None:
        """将 dataclass 列表保存到 MySQL 指定表中。

        Args:
            data: dataclass 对象列表
            table_name: 存入的表名（如 'entities'）
            if_exists: 处理已存在表的方式 ('fail', 'replace', 'append')
        """
        if not data:
            logger.warning(f"空数据，跳过向表 {table_name} 保存")
            return

        # 将 dataclass 转为 dict 列表
        records = []
        for item in data:
            d = asdict(item)
            # 将 list/dict 等复杂字段转为 JSON 字符串
            for key, value in d.items():
                if isinstance(value, (list, dict)):
                    d[key] = json.dumps(value, ensure_ascii=False)
            records.append(d)

        df = pd.DataFrame(records)

        try:
            # 使用 to_sql 插入
            df.to_sql(name=table_name, con=self.engine, if_exists=if_exists, index=False)
            logger.info(f"成功将 {len(data)} 条记录插入 MySQL 表中: {table_name}")
        except Exception as e:
            logger.error(f"插入 MySQL 失败 [{table_name}]: {e}")
            raise

    def read_df(self, table_name: str) -> pd.DataFrame:
        """从 MySQL 表中读取所有数据为 DataFrame。
        
        Args:
            table_name: 要读取的表名
            
        Returns:
            查询结果组成的 pd.DataFrame。如果表不存在或失败则返回空 DataFrame。
        """
        try:
            df = pd.read_sql_table(table_name, con=self.engine)
            logger.info(f"成功从 MySQL 表 {table_name} 读取了 {len(df)} 条记录")
            return df
        except Exception as e:
            logger.warning(f"读取 MySQL 表 {table_name} 时发生异常 (可能表不存在): {e}")
            return pd.DataFrame()

    def create_table(self, table_name: str, schema_sql: str) -> None:
        """执行原生 SQL 建表。
        注意：save 方法默认基于 Pandas 具有如果不存在则建表 (if_exists="append") 的能力，
        所以普通场景不需要手动调用建表。如果需要自定义索引或字段类型等精确结构，可调用此方法。
        
        Args:
            table_name: 要建表的表名（仅用于日志提示）
            schema_sql: 完整的 CREATE TABLE SQL 语句
        """
        from sqlalchemy import text
        try:
            with self.engine.begin() as conn:
                conn.execute(text(schema_sql))
            logger.info(f"成功建表: {table_name}")
        except Exception as e:
            logger.error(f"建表失败 [{table_name}]: {e}")
            raise

    def drop_table(self, table_name: str) -> None:
        """从 MySQL 中删除指定表。
        
        Args:
            table_name: 要删除的具体表名
        """
        from sqlalchemy import text
        try:
             with self.engine.begin() as conn:
                 conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
             logger.info(f"成功删除表: {table_name}")
        except Exception as e:
             logger.error(f"删表失败 [{table_name}]: {e}")
             raise

