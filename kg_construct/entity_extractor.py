"""
Step 3: 实体关系抽取

使用 LLM 从每个 TextUnit 中并发抽取实体和关系。
"""

import asyncio
import json
import logging
import uuid

# 所需配置
from common.config.models.chat_model_config import ChatModelConfig
from common.llm.chat_model import LitellmChatModel
from common.config.models.entity_extractor_config import EntityExtractorConfig

# 数据类型
from common.models.entity import Entity
from common.models.relationship import Relationship
from common.models.text_unit import TextUnit

from common.prompts.kg_construct.extract_graph import GRAPH_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


async def extract_graph(
    text_units: list[TextUnit],
    llm_config: ChatModelConfig,
    entity_extractor_config: EntityExtractorConfig,
) -> tuple[list[Entity], list[Relationship]]:
    """从文本块中并发抽取实体和关系。

    Args:
        text_units: 文本块列表
        llm_config: LLM 配置
        entity_extractor_config: 实体抽取配置

    Returns:
        (原始实体列表, 原始关系列表) — 未去重
    """
        
    entity_types_str = ", ".join(entity_extractor_config.entity_types)
    llm = LitellmChatModel(llm_config)
    semaphore = asyncio.Semaphore(llm_config.concurrent_requests)

    all_entities: list[Entity] = []
    all_relationships: list[Relationship] = []

    async def _extract_one(text_unit: TextUnit):
        async with semaphore:
            prompt = GRAPH_EXTRACTION_PROMPT.format(
                entity_types=entity_types_str,
                input_text=text_unit.text,
                tuple_delimiter=entity_extractor_config.tuple_delimiter,
                record_delimiter=entity_extractor_config.record_delimiter,
                completion_delimiter=entity_extractor_config.completion_delimiter
            )

            try:
                # LitellmChatModel.chat 是同步的，放到线程池执行
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, llm.chat, prompt
                )
                content = response.output.content
                result = _parse_llm_output(
                    content,
                    entity_extractor_config.tuple_delimiter,
                    entity_extractor_config.record_delimiter,
                    entity_extractor_config.completion_delimiter
                )

                entities, relationships = _build_models(
                    result, text_unit.id
                )
                return entities, relationships

            except Exception as e:
                logger.warning(
                    f"抽取失败 (text_unit={text_unit.id[:8]}): {e}"
                )
                return [], []

    # 并发执行所有抽取任务
    tasks = [_extract_one(tu) for tu in text_units]
    results = await asyncio.gather(*tasks)

    for entities, relationships in results:
        all_entities.extend(entities)
        all_relationships.extend(relationships)

    logger.info(
        f"抽取完成: {len(all_entities)} 个原始实体, "
        f"{len(all_relationships)} 个原始关系"
    )
    return all_entities, all_relationships


def _parse_llm_output(
    content: str,
    tuple_delimiter: str = "<|>",
    record_delimiter: str = "##",
    completion_delimiter: str = "<|COMPLETE|>"
) -> dict:
    """解析 LLM 输出的分隔符格式的元组。"""
    content = content.replace(completion_delimiter, "").strip()
    records = content.split(record_delimiter)

    entities = []
    relationships = []

    for record in records:
        record = record.strip()
        if not record:
            continue
        
        # 剥离前后的圆括号
        if record.startswith('(') and record.endswith(')'):
            record = record[1:-1]
            
        parts = [p.strip() for p in record.split(tuple_delimiter)]
        if not parts:
            continue
            
        type_str = parts[0].strip('"').strip("'").lower()
            
        if type_str == "entity" and len(parts) >= 4:
            entities.append({
                "name": parts[1].strip('"').strip("'"),
                "type": parts[2].strip('"').strip("'"),
                "description": parts[3].strip('"').strip("'")
            })
        elif type_str == "relationship" and len(parts) >= 5:
            relationships.append({
                "source": parts[1].strip('"').strip("'"),
                "target": parts[2].strip('"').strip("'"),
                "description": parts[3].strip('"').strip("'"),
                "weight": parts[4].strip('"').strip("'")
            })
            
    if not entities and not relationships:
        logger.warning(f"无法解析或未提取到实体: {content[:200]}")
        
    return {"entities": entities, "relationships": relationships}


def _build_models(
    result: dict, text_unit_id: str
) -> tuple[list[Entity], list[Relationship]]:
    """将解析后的 JSON 转换为 Entity 和 Relationship 对象。"""
    entities: list[Entity] = []
    relationships: list[Relationship] = []

    for e in result.get("entities", []):
        entity = Entity(
            id=str(uuid.uuid4()),
            title=e.get("name", "").strip().upper(),  # 标准化为大写
            type=e.get("type", "").strip().upper(),
            description=e.get("description", ""),
            text_unit_ids=[text_unit_id],
        )
        if entity.title:  # 跳过空实体
            entities.append(entity)

    for r in result.get("relationships", []):
        try:
            weight = float(r.get("weight", 1.0))
        except ValueError:
            weight = 1.0

        rel = Relationship(
            id=str(uuid.uuid4()),
            source=r.get("source", "").strip().upper(),
            target=r.get("target", "").strip().upper(),
            description=r.get("description", ""),
            weight=weight,
            text_unit_ids=[text_unit_id],
        )
        if rel.source and rel.target:  # 跳过不完整关系
            relationships.append(rel)

    return entities, relationships
