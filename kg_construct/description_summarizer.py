"""
Step 4: 描述合并去重

在 step3 用大模型提取实体、关系之后，此时得到了原始的实体，但是其中可能会有很多同名的实体，
因此需要对同名实体的描述进行合并，生成新的实体描述

将同名实体和相同 (source, target) 关系的描述合并。
"""

import asyncio
import logging
import uuid
from collections import defaultdict

from common.config.models.chat_model_config import ChatModelConfig
from common.config.models.description_summarizer_config import (
    DescriptionSummarizerConfig,
)
from common.llm.chat_model import LitellmChatModel

from common.models.entity import Entity
from common.models.relationship import Relationship

from common.prompts.summarize_descriptions import SUMMARIZE_PROMPT

logger = logging.getLogger(__name__)


async def summarize_descriptions(
    raw_entities: list[Entity],
    raw_relationships: list[Relationship],
    llm_config: ChatModelConfig,
    description_summarizer_config: DescriptionSummarizerConfig,
) -> tuple[list[Entity], list[Relationship]]:
    """合并去重实体和关系的描述。

    Args:
        raw_entities: 原始实体列表（可能有同名重复）
        raw_relationships: 原始关系列表（可能有重复 source-target）
        llm_config: LLM 配置

    Returns:
        (去重后的实体列表, 去重后的关系列表)
    """
    llm = LitellmChatModel(llm_config)
    concat_threshold = description_summarizer_config.concat_threshold
    semaphore = asyncio.Semaphore(llm_config.concurrent_requests)

    entities = await _merge_entities(raw_entities, llm, concat_threshold, semaphore)
    relationships = await _merge_relationships(raw_relationships, llm, concat_threshold, semaphore)

    logger.info(
        f"合并完成: {len(raw_entities)} → {len(entities)} 实体, "
        f"{len(raw_relationships)} → {len(relationships)} 关系"
    )
    return entities, relationships


async def _merge_entities(
    raw_entities: list[Entity],
    llm: LitellmChatModel,
    concat_threshold: int,
    semaphore: asyncio.Semaphore,
) -> list[Entity]:
    """按 title 分组合并实体。"""
    grouped: dict[str, list[Entity]] = defaultdict(list)
    for e in raw_entities:
        grouped[e.title].append(e)

    merged: list[Entity] = []
    tasks = []

    for title, group in grouped.items():
        if len(group) == 1:
            # 单条直接保留
            entity = group[0]
            entity.id = str(uuid.uuid4())
            merged.append(entity)
        else:
            tasks.append(_merge_entity_group(title, group, llm, concat_threshold, semaphore))

    if tasks:
        results = await asyncio.gather(*tasks)
        merged.extend(results)

    return merged


async def _merge_entity_group(
    title: str,
    group: list[Entity],
    llm: LitellmChatModel,
    concat_threshold: int,
    semaphore: asyncio.Semaphore,
) -> Entity:
    """合并同名实体组。"""
    descriptions = [e.description for e in group if e.description]
    all_text_unit_ids = []
    for e in group:
        all_text_unit_ids.extend(e.text_unit_ids)

    # 取最常见的类型
    types = [e.type for e in group if e.type]
    entity_type = max(set(types), key=types.count) if types else ""

    if len(descriptions) <= concat_threshold:
        merged_desc = "; ".join(descriptions)
    else:
        merged_desc = await _llm_summarize(title, descriptions, llm, semaphore)

    return Entity(
        id=str(uuid.uuid4()),
        title=title,
        type=entity_type,
        description=merged_desc,
        text_unit_ids=list(set(all_text_unit_ids)),
    )


async def _merge_relationships(
    raw_relationships: list[Relationship],
    llm: LitellmChatModel,
    concat_threshold: int,
    semaphore: asyncio.Semaphore,
) -> list[Relationship]:
    """按 (source, target) 分组合并关系。"""
    grouped: dict[tuple[str, str], list[Relationship]] = defaultdict(list)
    for r in raw_relationships:
        key = (r.source, r.target)
        grouped[key].append(r)

    merged: list[Relationship] = []
    tasks = []

    for (source, target), group in grouped.items():
        if len(group) == 1:
            rel = group[0]
            rel.id = str(uuid.uuid4())
            merged.append(rel)
        else:
            tasks.append(
                _merge_relationship_group(source, target, group, llm, concat_threshold, semaphore)
            )

    if tasks:
        results = await asyncio.gather(*tasks)
        merged.extend(results)

    return merged


async def _merge_relationship_group(
    source: str,
    target: str,
    group: list[Relationship],
    llm: LitellmChatModel,
    concat_threshold: int,
    semaphore: asyncio.Semaphore,
) -> Relationship:
    """合并同一对 source-target 的关系。"""
    descriptions = [r.description for r in group if r.description]
    total_weight = sum(r.weight for r in group)
    all_text_unit_ids = []
    for r in group:
        all_text_unit_ids.extend(r.text_unit_ids)

    if len(descriptions) <= concat_threshold:
        merged_desc = "; ".join(descriptions)
    else:
        rel_name = f"{source} -> {target}"
        merged_desc = await _llm_summarize(rel_name, descriptions, llm, semaphore)

    return Relationship(
        id=str(uuid.uuid4()),
        source=source,
        target=target,
        description=merged_desc,
        weight=total_weight,
        text_unit_ids=list(set(all_text_unit_ids)),
    )


async def _llm_summarize(
    entity_name: str,
    descriptions: list[str],
    llm: LitellmChatModel,
    semaphore: asyncio.Semaphore,
) -> str:
    """调用 LLM 合并多段描述。"""
    async with semaphore:
        numbered = "\n".join(
            f"{i + 1}. {desc}" for i, desc in enumerate(descriptions)
        )
        prompt = SUMMARIZE_PROMPT.format(
            entity_name=entity_name,
            description_list=numbered
        )

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, llm.chat, prompt)
        return response.output.content.strip()
