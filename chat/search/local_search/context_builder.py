import pandas as pd
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    构建混合上下文供 Local Search 使用。
    根据指定的 token 比例，从实体、关系、文本、社区报告中截取数据组装。
    """

    def __init__(self, entities_df: pd.DataFrame, relationships_df: pd.DataFrame, 
                 text_units_df: pd.DataFrame, community_reports_df: pd.DataFrame):
        self.entities = entities_df
        self.relationships = relationships_df
        self.text_units = text_units_df
        self.reports = community_reports_df

    def build_context(self, matched_entities: List[str], max_tokens: int = 12000, 
                      community_prop: float = 0.25, text_unit_prop: float = 0.50) -> str:
        """根据匹配的实体 ID 列表，提取并组装上下文数据"""
        # 1. 计算不同部分的 Token 预算
        community_budget = int(max_tokens * community_prop)
        text_unit_budget = int(max_tokens * text_unit_prop)
        entity_rel_budget = max_tokens - community_budget - text_unit_budget

        # 2. 提取并格式化（需要完善这部分的过滤与截断逻辑）
        community_context = self._build_community_context(matched_entities, community_budget)
        entity_rel_context = self._build_entity_rel_context(matched_entities, entity_rel_budget)
        text_unit_context = self._build_text_unit_context(matched_entities, text_unit_budget)

        # 3. 拼装为最终使用的字符串
        final_context = f"----- 社区报告 -----\n{community_context}\n\n" \
                        f"----- 实体与关系 -----\n{entity_rel_context}\n\n" \
                        f"----- 回溯来源文本 -----\n{text_unit_context}"
        return final_context

    def _build_community_context(self, entities: List[str], budget_tokens: int) -> str:
        if self.entities is None or self.reports is None or self.entities.empty or self.reports.empty:
            return ""
        
        # 找到这些实体属于哪些社区
        matched_rows = self.entities[self.entities['title'].isin(entities) | self.entities['id'].isin(entities)]
        community_ids = set()
        for c_ids in matched_rows['community_ids'].dropna():
            if isinstance(c_ids, str):
                import json
                try:
                    # 优先使用 json 解析，因为 MySQL 存储的是 json.dumps 后的结果
                    c_ids = json.loads(c_ids)
                except:
                    import ast
                    try:
                        c_ids = ast.literal_eval(c_ids)
                    except:
                        c_ids = []
            if isinstance(c_ids, list):
                community_ids.update(c_ids)
                
        reports = self.reports[self.reports['community_id'].isin(list(community_ids))]
        # 可以按 rank 排序
        if 'rank' in reports.columns:
            reports = reports.sort_values(by='rank', ascending=False)
            
        context_parts = []
        current_tokens = 0
        for _, row in reports.iterrows():
            title = row.get('title', '')
            summary = row.get('summary', '')
            report_text = f"Title: {title}\nSummary: {summary}\n"
            tokens = self._estimate_tokens(report_text)
            if current_tokens + tokens > budget_tokens:
                break
            context_parts.append(report_text)
            current_tokens += tokens
            
        return "\n".join(context_parts)

    def _build_entity_rel_context(self, entities: List[str], budget_tokens: int) -> str:
        if self.entities is None or self.relationships is None or self.entities.empty or self.relationships.empty:
            return ""
        
        # 实体本身
        matched_entities = self.entities[self.entities['title'].isin(entities) | self.entities['id'].isin(entities)]
        entity_ids = set(matched_entities['id'].dropna())
        
        # 关联关系
        matched_rels = self.relationships[
            self.relationships['source'].isin(entity_ids) | 
            self.relationships['target'].isin(entity_ids)
        ]
        
        context_parts = []
        current_tokens = 0
        
        # 加入实体描述
        for _, row in matched_entities.iterrows():
            text = f"Entity: {row.get('title', '')} ({row.get('type', '')})\nDesc: {row.get('description', '')}\n"
            tokens = self._estimate_tokens(text)
            if current_tokens + tokens > budget_tokens / 2: # 实体最多占一半预算
                break
            context_parts.append(text)
            current_tokens += tokens
            
        # 加入关系
        for _, row in matched_rels.iterrows():
            text = f"Rel: {row.get('source', '')} -> {row.get('target', '')}\nDesc: {row.get('description', '')}\n"
            tokens = self._estimate_tokens(text)
            if current_tokens + tokens > budget_tokens:
                break
            context_parts.append(text)
            current_tokens += tokens
            
        return "\n".join(context_parts)

    def _build_text_unit_context(self, entities: List[str], budget_tokens: int) -> str:
        if self.entities is None or self.text_units is None or self.entities.empty or self.text_units.empty:
            return ""
        
        matched_entities = self.entities[self.entities['title'].isin(entities) | self.entities['id'].isin(entities)]
        text_unit_ids = set()
        for t_ids in matched_entities['text_unit_ids'].dropna():
            if isinstance(t_ids, str):
                import json
                try:
                    t_ids = json.loads(t_ids)
                except:
                    import ast
                    try:
                        t_ids = ast.literal_eval(t_ids)
                    except:
                        t_ids = []
            if isinstance(t_ids, list):
                text_unit_ids.update(t_ids)
                
        matched_texts = self.text_units[self.text_units['id'].isin(text_unit_ids)]
        
        context_parts = []
        current_tokens = 0
        for _, row in matched_texts.iterrows():
            text = f"Text [{row.get('id', '')}]: {row.get('text', '')}\n"
            tokens = self._estimate_tokens(text)
            if current_tokens + tokens > budget_tokens:
                break
            context_parts.append(text)
            current_tokens += tokens
            
        return "\n".join(context_parts)

    def _estimate_tokens(self, text: str) -> int:
        """简易 token 结算方法"""
        return int(len(str(text)) / 1.5)
