"""
Step 8: Embedding 生成与存储

将实体描述向量化并存入 Milvus。
"""

import logging

from pymilvus import (
    CollectionSchema,
    DataType,
    FieldSchema,
    MilvusClient,
)

from common.config.models.embedding_model_config import EmbeddingModelConfig
from common.models.entity import Entity

logger = logging.getLogger(__name__)

ENTITY_COLLECTION = "entity_description"


def generate_and_store_embeddings(
    entities: list[Entity],
    embedding_config: EmbeddingModelConfig,
    milvus_uri: str,
    milvus_db_name: str = "kgrag",
    collection_name: str = ENTITY_COLLECTION,
) -> None:
    """为实体生成 Embedding 并存储到 Milvus。

    Args:
        entities: 实体列表
        embedding_config: Embedding 模型配置
        milvus_uri: Milvus 连接地址
        milvus_db_name: Milvus 数据库名
        collection_name: Collection 名称
    """
    if not entities:
        logger.warning("实体列表为空，跳过 Embedding")
        return

    # 1. 生成 Embedding 向量
    logger.info(f"开始生成 {len(entities)} 个实体的 Embedding...")

    from litellm import embedding as litellm_embedding

    texts = [e.embedding_text for e in entities]
    vectors: list[list[float]] = []

    # 分批处理
    batch_size = embedding_config.batch_size
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = litellm_embedding(
            model=embedding_config.model_name,
            input=batch,
            api_base=embedding_config.api_base,
            api_key=embedding_config.api_key,
        )
        for item in response.data:
            vectors.append(item["embedding"])

        logger.info(f"Embedding 进度: {min(i + batch_size, len(texts))}/{len(texts)}")

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
                dim=embedding_config.vector_dim,
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
        for entity, vector in zip(entities, vectors)
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
