"""
kg_construct Pipeline — 知识图谱构建主编排

8 步流水线：文档 → 分块 → 抽取 → 合并 → 定稿 → 社区 → 报告 → Embedding
"""

import asyncio
import logging
import time

from common.config.models.chat_model_config import ChatModelConfig
from common.config.models.embedding_model_config import EmbeddingModelConfig

from kg_construct.document_loader import load_documents
from kg_construct.chunker import create_text_units
from kg_construct.entity_extractor import extract_graph
from kg_construct.description_summarizer import summarize_descriptions
from kg_construct.graph_finalizer import finalize_graph
from kg_construct.community_detector import create_communities
from kg_construct.report_generator import create_community_reports
from kg_construct.embedding_generator import generate_and_store_embeddings
from kg_construct.storage_helper import save_parquet

logger = logging.getLogger(__name__)


async def run_pipeline(
    input_dir: str,
    output_dir: str,
    llm_config: ChatModelConfig | None = None,
    embedding_config: EmbeddingModelConfig | None = None,
    chunk_size: int = 300,
    chunk_overlap: int = 100,
    entity_types: list[str] | None = None,
    community_max_levels: int = 3,
    milvus_uri: str = "http://localhost:19530",
    milvus_db_name: str = "kgrag",
) -> dict:
    """执行完整的知识图谱构建 Pipeline。

    Args:
        input_dir: 原始文档输入目录
        output_dir: Parquet 输出目录
        llm_config: Chat LLM 配置（None 将使用默认值）
        embedding_config: Embedding 配置（None 将使用默认值）
        chunk_size: 分块 token 数
        chunk_overlap: 分块重叠 token 数
        entity_types: 实体类型列表
        community_max_levels: 社区最大层级
        milvus_uri: Milvus 连接地址
        milvus_db_name: Milvus 数据库名

    Returns:
        包含各阶段统计信息的 dict
    """
    if llm_config is None:
        llm_config = ChatModelConfig()
    if embedding_config is None:
        embedding_config = EmbeddingModelConfig()

    total_start = time.time()
    stats = {}

    # ==========================================
    # Step 1: 文档加载
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 1/8: 文档加载")
    t0 = time.time()
    documents = load_documents(input_dir)
    save_parquet(documents, "documents.parquet", output_dir)
    stats["documents"] = len(documents)
    logger.info(f"Step 1 完成 ({time.time() - t0:.1f}s)")

    if not documents:
        logger.error("没有加载到任何文档，Pipeline 终止")
        return stats

    # ==========================================
    # Step 2: 文档分块
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 2/8: 文档分块")
    t0 = time.time()
    text_units = create_text_units(documents, chunk_size, chunk_overlap)
    stats["text_units"] = len(text_units)
    logger.info(f"Step 2 完成 ({time.time() - t0:.1f}s)")

    # ==========================================
    # Step 3: 实体关系抽取（LLM）
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 3/8: 实体关系抽取 (LLM)")
    t0 = time.time()
    raw_entities, raw_relationships = await extract_graph(
        text_units, llm_config, entity_types
    )
    stats["raw_entities"] = len(raw_entities)
    stats["raw_relationships"] = len(raw_relationships)
    logger.info(f"Step 3 完成 ({time.time() - t0:.1f}s)")

    if not raw_entities:
        logger.error("未抽取到任何实体，Pipeline 终止")
        return stats

    # ==========================================
    # Step 4: 描述合并去重（LLM）
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 4/8: 描述合并去重 (LLM)")
    t0 = time.time()
    entities, relationships = await summarize_descriptions(
        raw_entities, raw_relationships, llm_config
    )
    stats["entities"] = len(entities)
    stats["relationships"] = len(relationships)
    logger.info(f"Step 4 完成 ({time.time() - t0:.1f}s)")

    # ==========================================
    # Step 5: 图定稿
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 5/8: 图定稿 (计算 rank)")
    t0 = time.time()
    entities, relationships, text_units = finalize_graph(
        entities, relationships, text_units
    )
    save_parquet(entities, "entities.parquet", output_dir)
    save_parquet(relationships, "relationships.parquet", output_dir)
    save_parquet(text_units, "text_units.parquet", output_dir)
    logger.info(f"Step 5 完成 ({time.time() - t0:.1f}s)")

    # ==========================================
    # Step 6: 社区发现
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 6/8: 社区发现 (Leiden)")
    t0 = time.time()
    communities = create_communities(
        entities, relationships, max_levels=community_max_levels
    )
    save_parquet(communities, "communities.parquet", output_dir)
    stats["communities"] = len(communities)
    logger.info(f"Step 6 完成 ({time.time() - t0:.1f}s)")

    # ==========================================
    # Step 7: 社区报告（LLM）
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 7/8: 社区报告生成 (LLM)")
    t0 = time.time()
    community_reports = await create_community_reports(
        communities, entities, relationships, llm_config
    )
    save_parquet(community_reports, "community_reports.parquet", output_dir)
    stats["community_reports"] = len(community_reports)
    logger.info(f"Step 7 完成 ({time.time() - t0:.1f}s)")

    # ==========================================
    # Step 8: Embedding → Milvus
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 8/8: Embedding 生成与存储")
    t0 = time.time()
    generate_and_store_embeddings(
        entities, embedding_config, milvus_uri, milvus_db_name
    )
    logger.info(f"Step 8 完成 ({time.time() - t0:.1f}s)")

    # ==========================================
    # 完成
    # ==========================================
    total_time = time.time() - total_start
    logger.info("=" * 50)
    logger.info(f"🎉 Pipeline 完成! 总耗时: {total_time:.1f}s")
    logger.info(f"统计: {stats}")

    return stats


def run(
    input_dir: str = "./data/input",
    output_dir: str = "./data/output",
    **kwargs,
) -> dict:
    """同步入口，内部使用 asyncio.run 执行 Pipeline。"""
    return asyncio.run(
        run_pipeline(input_dir=input_dir, output_dir=output_dir, **kwargs)
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    run()
