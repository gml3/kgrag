"""
Milvus 存储辅助

提供面向对象的 Milvus 向量检索服务。
"""

import logging
from typing import List, Any, Optional

from pymilvus import MilvusClient
from common.config.models.milvus_config import MilvusConfig

logger = logging.getLogger(__name__)


class MilvusStorage:
    """Milvus 向量数据库存储与检索服务"""

    def __init__(self, config: MilvusConfig):
        """初始化 Milvus 客户端。
        
        Args:
            config: Milvus 配置对象
        """
        self.config = config
        self.client = MilvusClient(
            uri=f"http://{config.host}:{config.port}",
            db_name=config.db_name
        )

    def search(
        self, 
        collection_name: str, 
        data: List[Any], 
        limit: int = 10, 
        output_fields: Optional[List[str]] = None
    ) -> List[List[dict]]:
        """在向量库中执行搜索。

        Args:
            collection_name: 集合名称
            data: 查询向量列表
            limit: 返回结果数量限制
            output_fields: 输出字段列表

        Returns:
            搜索结果列表
        """
        try:
            res = self.client.search(
                collection_name=collection_name,
                data=data,
                limit=limit,
                output_fields=output_fields
            )
            return res
        except Exception as e:
            logger.error(f"Milvus 搜索失败 [{collection_name}]: {e}")
            raise
