from dataclasses import dataclass


@dataclass
class CommunityConfig:
    """
    社区发现配置
    """
    
    max_levels: int = 10
    """最大层级数"""

    max_cluster_size: int = 10
    """聚类的最大数量"""

    seed: int = 42
    """随机种子"""
    