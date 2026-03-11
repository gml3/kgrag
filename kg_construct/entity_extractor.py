"""
Step 3: 实体关系抽取

使用 LLM 从每个 TextUnit 中并发抽取实体和关系。
"""

import asyncio
import json
import logging
import uuid

from common.config.models.chat_model_config import ChatModelConfig
from common.llm.chat_model import LitellmChatModel
from common.models.entity import Entity
from common.models.relationship import Relationship
from common.models.text_unit import TextUnit
from kg_construct.prompts.extract_graph import GRAPH_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


async def extract_graph(
    text_units: list[TextUnit],
    llm_config: ChatModelConfig,
    entity_types: list[str] | None = None,
    tuple_delimiter: str | None = None,
    record_delimiter: str | None = None,
    completion_delimiter: str | None = None
) -> tuple[list[Entity], list[Relationship]]:
    """从文本块中并发抽取实体和关系。

    Args:
        text_units: 文本块列表
        llm_config: LLM 配置
        entity_types: 实体类型列表

    Returns:
        (原始实体列表, 原始关系列表) — 未去重
    """
    if entity_types is None:
        entity_types = ["人", "组织", "位置", "事件"]

    if tuple_delimiter is None:
        tuple_delimiter = "<|>"
        
    if record_delimiter is None:
        record_delimiter = "##"
    
    if completion_delimiter is None:
        completion_delimiter = "<|COMPLETE|>"
        
    entity_types_str = ", ".join(entity_types)
    llm = LitellmChatModel(llm_config)
    semaphore = asyncio.Semaphore(llm_config.concurrent_requests)

    all_entities: list[Entity] = []
    all_relationships: list[Relationship] = []

    async def _extract_one(text_unit: TextUnit):
        async with semaphore:
            prompt = GRAPH_EXTRACTION_PROMPT.format(
                entity_types=entity_types_str,
                input_text=text_unit.text,
                tuple_delimiter=tuple_delimiter,
                record_delimiter=record_delimiter,
                completion_delimiter=completion_delimiter
            )

            try:
                # LitellmChatModel.chat 是同步的，放到线程池执行
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, llm.chat, prompt
                )
                content = response.output.content
                result = _parse_llm_output(content)

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


def _parse_llm_output(content: str) -> dict:
    """解析 LLM 输出的 JSON。"""
    # 尝试提取 JSON 块
    content = content.strip()

    # 处理 markdown 代码块包裹
    if content.startswith("```"):
        lines = content.split("\n")
        # 去掉首尾的 ``` 行
        lines = [l for l in lines if not l.strip().startswith("```")]
        content = "\n".join(lines)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 尝试找到 JSON 对象
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(content[start:end])
            except json.JSONDecodeError:
                pass

        logger.warning(f"无法解析 LLM 输出: {content[:200]}")
        return {"entities": [], "relationships": []}


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
        rel = Relationship(
            id=str(uuid.uuid4()),
            source=r.get("source", "").strip().upper(),
            target=r.get("target", "").strip().upper(),
            description=r.get("description", ""),
            weight=float(r.get("weight", 1.0)),
            text_unit_ids=[text_unit_id],
        )
        if rel.source and rel.target:  # 跳过不完整关系
            relationships.append(rel)

    return entities, relationships
