"""A file containing prompts definition."""

SUMMARIZE_PROMPT = """
你是一个有帮助的助手，负责生成以下提供的数据的综合摘要。
给定一个或多个实体，以及与同一实体或实体组相关的描述列表。
请将所有这些描述连接成一个单一的、全面的描述。确保包含从所有描述中收集的信息。
如果提供的描述相互矛盾，请解决矛盾并提供一个单一的、连贯的摘要。
确保使用第三人称撰写，并包含实体名称，以便我们有完整的上下文。

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""
