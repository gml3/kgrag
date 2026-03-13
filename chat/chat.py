import os
import sys
import logging

# 确保在根目录下可以导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.config.models.local_search_config import LocalSearchConfig
from common.config.models.mysql_config import MysqlConfig
from common.config.models.milvus_config import MilvusConfig
from common.config.models.embedding_model_config import EmbeddingModelConfig
from common.config.models.chat_model_config import ChatModelConfig
from common.llm.chat_model import LitellmChatModel
from chat.search.local_search.local_search import LocalSearch

# 配置简单的日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def run_real_test():
    """
    使用真实的数据库数据测试 local_search。
    请确保系统配置了以下服务均可访问：
    1. MySQL 数据库包含 KG 构建的表 (entities, relationships, text_units, community_reports)
    2. Milvus 向量库
    3. LLM/Embedding API Keys 已经设置在环境变量中
    """
    print(">>> 正在初始化配置...")
    config = LocalSearchConfig(
        chat_model=ChatModelConfig(),
        embedding_model=EmbeddingModelConfig(),
        milvus=MilvusConfig(),
        mysql=MysqlConfig(),
        collection_name="kgrag",
        max_tokens=6000,
        top_k=10
    )
    
    print(">>> 正在初始化 LLM...")
    llm = LitellmChatModel(config.chat_model)
    
    print(">>> 正在初始化 LocalSearch (这将从 MySQL 加载数据并连接 Milvus)...")
    try:
        search_engine = LocalSearch(llm=llm, config=config)
    except Exception as e:
        print(f"初始化失败: {e}")
        return
    
    # 设定一个测试用的 query。根据图谱的数据内容，此处我们先写一个通用的。
    query = "请总结关于江门公积金的核心问题与相关机构。"
    print(f"\n>>> 正在执行局部搜索...")
    print(f"Query: {query}\n")
    
    try:
        response = search_engine.search(query)
        print("========== 搜索回复 ==========")
        print(response.output.content if hasattr(response, 'output') else response)
        print("==============================")
    except Exception as e:
        print(f"搜索执行时失败: {e}")

if __name__ == "__main__":
    run_real_test()
