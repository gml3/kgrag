import logging
from pymilvus import connections, utility
import os
import sys

# 添加项目根目录到 sys.path 以便导入 common
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.config.models.milvus_config import MilvusConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_milvus_connection():
    config = MilvusConfig()
    
    logger.info(f"正在尝试连接到 Milvus...")
    logger.info(f"Host: {config.host}")
    # logger.info(f"Port: {config.port}")
    
    try:
        # 尝试建立连接
        connections.connect(
            alias="default", 
            host=config.host, 
            # port=config.port,
            timeout=5.0
        )
        logger.info("✅ 成功连接到 Milvus 服务器!")
        
        # 检查是否能够获取集合列表
        collections = utility.list_collections()
        logger.info(f"当前数据库中的 Collections 数量: {len(collections)}")
        logger.info(f"Collections 列表: {collections}")
        
    except Exception as e:
        logger.error(f"❌ 连接 Milvus 失败!")
        logger.error(f"错误信息: {e}")
    finally:
        # 断开连接
        try:
            connections.disconnect("default")
            logger.info("已断开与 Milvus 的连接")
        except Exception:
            pass

if __name__ == "__main__":
    test_milvus_connection()
