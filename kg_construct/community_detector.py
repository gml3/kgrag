"""
Step 6: 社区发现

使用 Leiden 算法在实体-关系图上进行层次聚类。
"""

import logging
import uuid
from collections import defaultdict

import networkx as nx
from graspologic.partition import hierarchical_leiden

from common.config.models.community_config import CommunityConfig

from common.models.community import Community
from common.models.entity import Entity
from common.models.relationship import Relationship

logger = logging.getLogger(__name__)


def create_communities(
    entities: list[Entity],
    relationships: list[Relationship],
    config: CommunityConfig,
) -> list[Community]:
    """执行 Leiden 算法发现层级社区结构。

    Args:
        entities: 实体列表
        relationships: 关系列表
        config: 社区发现配置

    Returns:
        Community 列表（多层级）
    """
    # 1. 构建 NetworkX 图
    G = nx.Graph()

    entity_by_title: dict[str, Entity] = {}
    for entity in entities:
        G.add_node(entity.title)
        entity_by_title[entity.title] = entity

    for rel in relationships:
        if rel.source in entity_by_title and rel.target in entity_by_title:
            G.add_edge(rel.source, rel.target, weight=rel.weight)

    if G.number_of_nodes() == 0:
        logger.warning("空图，跳过社区发现")
        return []

    # 2. 执行 hierarchical Leiden
    community_map = hierarchical_leiden(G, max_cluster_size=config.max_cluster_size, 
                                        random_seed=config.seed)

    # 3. 按 level 整理结果
    # community_map 返回 list of CommunityMapping(node, cluster, level, ...)
    level_clusters: dict[int, dict[int, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for mapping in community_map:
        node = mapping.node
        cluster = mapping.cluster
        level = mapping.level
        if level < config.max_levels:
            level_clusters[level][cluster].append(node)

    # 4. 构建 Community 对象
    # 建立关系反查表
    relationship_by_entity: dict[str, list[str]] = defaultdict(list)
    for rel in relationships:
        relationship_by_entity[rel.source].append(rel.id)
        relationship_by_entity[rel.target].append(rel.id)

    communities: list[Community] = []

    for level in sorted(level_clusters.keys()):
        clusters = level_clusters[level]
        for cluster_id, node_titles in clusters.items():
            # 找到每个节点对应的 Entity ID
            entity_ids = []
            rel_ids_set = set()
            for title in node_titles:
                if title in entity_by_title:
                    entity = entity_by_title[title]
                    entity_ids.append(entity.id)
                    # 添加该实体相关的关系
                    for rid in relationship_by_entity.get(title, []):
                        rel_ids_set.add(rid)

            community = Community(
                id=str(uuid.uuid4()),
                level=level,
                entity_ids=entity_ids,
                relationship_ids=list(rel_ids_set),
            )
            communities.append(community)

            # 反向关联：更新实体的 community_ids
            for title in node_titles:
                if title in entity_by_title:
                    entity_by_title[title].community_ids.append(community.id)

    logger.info(
        f"社区发现完成: {len(communities)} 个社区 "
        f"(共 {len(level_clusters)} 个层级)"
    )
    return communities
