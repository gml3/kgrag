"""
Step 7: 社区报告生成

使用 LLM 为每个社区生成摘要报告。
"""

import asyncio
import logging
import uuid

from common.config.models.chat_model_config import ChatModelConfig
from common.llm.chat_model import LitellmChatModel
from common.models.community import Community, CommunityReport
from common.models.entity import Entity
from common.models.relationship import Relationship

logger = logging.getLogger(__name__)

COMMUNITY_REPORT_PROMPT = """\
以下是一个社区（主题聚类）中的实体和关系信息。请为这个社区生成一份摘要报告。

## 社区内的实体：
{community_entities}

## 社区内的关系：
{community_relationships}

请按照以下 JSON 格式输出：
{{
  "title": "社区报告标题（概括核心主题）",
  "summary": "2-3句话的摘要",
  "full_content": "详细描述社区内的核心实体、它们之间的关系和主要主题"
}}

请直接输出 JSON，不要输出其他内容。
"""


async def create_community_reports(
    communities: list[Community],
    entities: list[Entity],
    relationships: list[Relationship],
    llm_config: ChatModelConfig,
) -> list[CommunityReport]:
    """为每个社区生成摘要报告。

    Args:
        communities: 社区列表
        entities: 实体列表
        relationships: 关系列表
        llm_config: LLM 配置

    Returns:
        CommunityReport 列表
    """
    llm = LitellmChatModel(llm_config)
    semaphore = asyncio.Semaphore(llm_config.concurrent_requests)

    # 构建查找表
    entity_map: dict[str, Entity] = {e.id: e for e in entities}
    rel_map: dict[str, Relationship] = {r.id: r for r in relationships}

    async def _generate_one(community: Community) -> CommunityReport | None:
        async with semaphore:
            # 汇总社区内的实体和关系信息
            entity_texts = []
            for eid in community.entity_ids:
                e = entity_map.get(eid)
                if e:
                    entity_texts.append(
                        f"- {e.title} ({e.type}): {e.description}"
                    )

            rel_texts = []
            for rid in community.relationship_ids:
                r = rel_map.get(rid)
                if r:
                    rel_texts.append(
                        f"- {r.source} → {r.target}: {r.description}"
                    )

            if not entity_texts:
                return None

            prompt = COMMUNITY_REPORT_PROMPT.format(
                community_entities="\n".join(entity_texts),
                community_relationships="\n".join(rel_texts) if rel_texts else "无",
            )

            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, llm.chat, prompt)
                content = response.output.content.strip()
                return _parse_report(content, community)
            except Exception as e:
                logger.warning(f"社区报告生成失败 (community={community.id[:8]}): {e}")
                return None

    tasks = [_generate_one(c) for c in communities]
    results = await asyncio.gather(*tasks)

    reports = [r for r in results if r is not None]

    # 计算 rank（基于社区内实体总 degree 的平均）
    for report in reports:
        community = next(c for c in communities if c.id == report.community_id)
        degrees = [entity_map[eid].rank for eid in community.entity_ids if eid in entity_map]
        report.rank = sum(degrees) / len(degrees) if degrees else 0.0

    logger.info(f"社区报告生成完成: {len(reports)} 份报告")
    return reports


def _parse_report(content: str, community: Community) -> CommunityReport:
    """解析 LLM 输出为 CommunityReport。"""
    import json

    # 清理 markdown 包裹
    if content.startswith("```"):
        lines = content.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        content = "\n".join(lines)

    try:
        start = content.find("{")
        end = content.rfind("}") + 1
        data = json.loads(content[start:end])
    except (json.JSONDecodeError, ValueError):
        # 如果解析失败，把整个内容作为 full_content
        data = {"title": "社区报告", "summary": "", "full_content": content}

    return CommunityReport(
        id=str(uuid.uuid4()),
        community_id=community.id,
        title=data.get("title", ""),
        summary=data.get("summary", ""),
        full_content=data.get("full_content", ""),
    )
