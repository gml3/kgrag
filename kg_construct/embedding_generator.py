"""
Step 8: Embedding 生成与存储

将实体描述向量化（调用自部署 bge-m3）并存入 Milvus。
"""

import logging

import requests
from pymilvus import (
    CollectionSchema,
    DataType,
    FieldSchema,
    MilvusClient,
)

from common.config.models.embedding_model_config import EmbeddingModelConfig
from common.config.models.milvus_config import MilvusConfig
from common.models.entity import Entity

logger = logging.getLogger(__name__)


from common.embeddings.client import convert_text_to_vec


def generate_and_store_embeddings(
    entities: list[Entity],
    embedding_config: EmbeddingModelConfig,
    milvus_uri: str,
    milvus_db_name: str = "kgrag",
    collection_name: str = "entity_description",
    batch_size: int = 32,
) -> None:
    """为实体生成 Embedding 并存储到 Milvus。

    Args:
        entities: 实体列表
        embedding_config: Embedding 模型配置
        milvus_uri: Milvus 连接地址
        milvus_db_name: Milvus 数据库名
        collection_name: Collection 名称
        batch_size: 批量处理大小
    """
    if not entities:
        logger.warning("实体列表为空，跳过 Embedding")
        return

    # 1. 分批生成 Embedding 向量
    logger.info(f"开始生成 {len(entities)} 个实体的 Embedding...")

    texts = [e.embedding_text for e in entities]
    all_dense_vectors: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        dense_vectors, _ = convert_text_to_vec(batch, embedding_config)
        all_dense_vectors.extend(dense_vectors)
        logger.info(f"Embedding 进度: {min(i + batch_size, len(texts))}/{len(texts)}")

    # 获取向量维度
    vector_dim = len(all_dense_vectors[0])
    logger.info(f"向量维度: {vector_dim}")

    # 2. 连接 Milvus 并写入
    client = MilvusClient(uri=milvus_uri, db_name=milvus_db_name)

    # 如果 collection 已存在则删除重建
    if client.has_collection(collection_name):
        client.drop_collection(collection_name)
        logger.info(f"已删除旧 collection: {collection_name}")

    # 创建 collection
    schema = CollectionSchema(
        fields=[
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=64,
            ),
            FieldSchema(
                name="text",
                dtype=DataType.VARCHAR,
                max_length=8192,
            ),
            FieldSchema(
                name="entity_title",
                dtype=DataType.VARCHAR,
                max_length=512,
            ),
            FieldSchema(
                name="entity_type",
                dtype=DataType.VARCHAR,
                max_length=128,
            ),
            FieldSchema(
                name="vector",
                dtype=DataType.FLOAT_VECTOR,
                dim=vector_dim,
            ),
        ],
        description="Entity description embeddings",
    )

    client.create_collection(
        collection_name=collection_name,
        schema=schema,
    )

    # 插入数据
    data = [
        {
            "id": entity.id,
            "text": entity.embedding_text[:8192],
            "entity_title": entity.title[:512],
            "entity_type": entity.type[:128],
            "vector": vector,
        }
        for entity, vector in zip(entities, all_dense_vectors)
    ]

    client.insert(collection_name=collection_name, data=data)

    # 创建索引
    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="HNSW",
        metric_type="COSINE",
        params={"M": 16, "efConstruction": 256},
    )
    client.create_index(collection_name=collection_name, index_params=index_params)
    client.load_collection(collection_name=collection_name)

    logger.info(
        f"Milvus 写入完成: {len(data)} 条记录 → {collection_name}"
    )
