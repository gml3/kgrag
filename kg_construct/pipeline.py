"""
kg_construct Pipeline — 知识图谱构建主编排

8 步流水线：文档 → 分块 → 抽取 → 合并 → 定稿 → 社区 → 报告 → Embedding
"""

import asyncio
import logging
import time

# 配置
from common.config.models.kg_construct_config import KGConstructConfig

# 工作流
from kg_construct.document_loader import load_documents
from kg_construct.chunker import create_text_units
from kg_construct.entity_extractor import extract_graph
from kg_construct.description_summarizer import summarize_descriptions
from kg_construct.graph_finalizer import finalize_graph
from kg_construct.community_detector import create_communities
from kg_construct.report_generator import create_community_reports
from kg_construct.embedding_generator import generate_and_store_embeddings

# 存储类
from common.storage.mysql_storage import MysqlStorage

logger = logging.getLogger(__name__)


async def kg_construct_pipeline(
    config: KGConstructConfig,
) -> dict:
    """执行完整的知识图谱构建 Pipeline"""

    # 初始化 MySQL 存储服务
    mysql_storage = MysqlStorage(config.mysql)

    total_start = time.time()
    stats = {}

    # ==========================================
    # Step 1: 文档加载
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 1/8: 文档加载")
    t0 = time.time()
    documents = load_documents(config.documentloader)
    mysql_storage.save(documents, "documents")
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
    text_units = create_text_units(config.chunking, config.tokenizer, documents)
    stats["text_units"] = len(text_units)
    logger.info(f"Step 2 完成 ({time.time() - t0:.1f}s)")

    # ==========================================
    # Step 3: 实体关系抽取（LLM）
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 3/8: 实体关系抽取 (LLM)")
    t0 = time.time()
    raw_entities, raw_relationships = await extract_graph(
        text_units, config.chat_model, config.entity_extractor
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
        raw_entities, raw_relationships, config.chat_model, config.description_summarizer
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
    mysql_storage.save(entities, "entities")
    mysql_storage.save(relationships, "relationships")
    mysql_storage.save(text_units, "text_units")
    logger.info(f"Step 5 完成 ({time.time() - t0:.1f}s)")

    # ==========================================
    # Step 6: 社区发现
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 6/8: 社区发现 (Leiden)")
    t0 = time.time()
    communities = create_communities(
        entities, relationships, config.community_detector
    )
    # 更新存储中实体的社区 ID 关联
    mysql_storage.save(entities, "entities", if_exists="replace")
    mysql_storage.save(communities, "communities")
    stats["communities"] = len(communities)
    logger.info(f"Step 6 完成 ({time.time() - t0:.1f}s)")

    # ==========================================
    # Step 7: 社区报告（LLM）
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 7/8: 社区报告生成 (LLM)")
    t0 = time.time()
    community_reports = await create_community_reports(
        communities, entities, relationships, config.chat_model
    )
    mysql_storage.save(community_reports, "community_reports")
    stats["community_reports"] = len(community_reports)
    logger.info(f"Step 7 完成 ({time.time() - t0:.1f}s)")

    # ==========================================
    # Step 8: Embedding → Milvus
    # ==========================================
    logger.info("=" * 50)
    logger.info("Step 8/8: Embedding 生成与存储")
    t0 = time.time()
    generate_and_store_embeddings(
        entities, config.embedding_model, config.milvus
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


def run(config: KGConstructConfig | None = None) -> dict:
    """同步入口，内部使用 asyncio.run 执行 Pipeline。"""
    if config is None:
        config = KGConstructConfig()
    return asyncio.run(
        kg_construct_pipeline(config=config)
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    run()
