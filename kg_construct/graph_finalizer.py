"""
Step 5: 图定稿

使用 NetworkX 计算实体 rank（degree）和关系 rank（combined_degree），
并将 entity_ids/relationship_ids 反向关联到 text_units。
"""

import logging

import networkx as nx

from common.models.entity import Entity
from common.models.relationship import Relationship
from common.models.text_unit import TextUnit

logger = logging.getLogger(__name__)


def finalize_graph(
    entities: list[Entity],
    relationships: list[Relationship],
    text_units: list[TextUnit],
) -> tuple[list[Entity], list[Relationship], list[TextUnit]]:
    """图定稿：计算 rank 并关联 text_units。

    Args:
        entities: 去重后的实体列表
        relationships: 去重后的关系列表
        text_units: 文本块列表

    Returns:
        (更新后的 entities, relationships, text_units)
    """
    # 1. 构建 NetworkX 图，计算 degree
    G = nx.Graph()

    entity_by_title: dict[str, Entity] = {}
    for entity in entities:
        G.add_node(entity.title)
        entity_by_title[entity.title] = entity

    for rel in relationships:
        if rel.source in entity_by_title and rel.target in entity_by_title:
            G.add_edge(rel.source, rel.target, weight=rel.weight)

    # 2. 更新实体 rank = degree
    for entity in entities:
        entity.rank = float(G.degree(entity.title)) if entity.title in G else 0.0

    logger.info(f"实体 rank 计算完成 (最大 degree={max(e.rank for e in entities):.0f})")

    # 3. 更新关系 rank = source_degree + target_degree
    for rel in relationships:
        source_degree = G.degree(rel.source) if rel.source in G else 0
        target_degree = G.degree(rel.target) if rel.target in G else 0
        rel.rank = float(source_degree + target_degree)

    # 4. 反向关联：从 entity/relationship 的 text_unit_ids 反推到 text_unit 的 entity_ids
    text_unit_map: dict[str, TextUnit] = {tu.id: tu for tu in text_units}

    for entity in entities:
        for tu_id in entity.text_unit_ids:
            if tu_id in text_unit_map:
                text_unit_map[tu_id].entity_ids.append(entity.id)

    for rel in relationships:
        for tu_id in rel.text_unit_ids:
            if tu_id in text_unit_map:
                text_unit_map[tu_id].relationship_ids.append(rel.id)

    # 去重 entity_ids / relationship_ids
    for tu in text_units:
        tu.entity_ids = list(set(tu.entity_ids))
        tu.relationship_ids = list(set(tu.relationship_ids))

    logger.info(
        f"图定稿完成: {len(entities)} 实体, {len(relationships)} 关系, "
        f"{len(text_units)} 文本块已关联"
    )
    return entities, relationships, text_units
