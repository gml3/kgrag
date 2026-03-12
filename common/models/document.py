"""
Document — 原始文档模型
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Document:
    """原始文档的数据模型。

    存储文档的元信息和原始内容，用于溯源和追踪。
    """

    id: str
    """文档唯一标识, 通过uuid生成"""

    title: str = ""
    """文档标题, 通过文件名生成"""

    raw_content: str = ""
    """原始文本内容"""

    file_path: Optional[str] = None
    """源文件路径（可选）"""

    file_type: Optional[str] = None
    """文件类型（txt/pdf/csv/json 等）"""

    metadata: dict = field(default_factory=dict)
    """附加元信息"""
