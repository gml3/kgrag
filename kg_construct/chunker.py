"""
Step 2: 文档分块

将文档按固定 token 数切分为 TextUnit 列表。
"""

import logging
import uuid

import tiktoken

from common.models.document import Document
from common.models.text_unit import TextUnit

logger = logging.getLogger(__name__)

# 默认使用 cl100k_base 编码（GPT-4/3.5 同款，通用性好）
DEFAULT_ENCODING = "cl100k_base"


def create_text_units(
    documents: list[Document],
    chunk_size: int = 300,
    chunk_overlap: int = 100,
    encoding_name: str = DEFAULT_ENCODING,
) -> list[TextUnit]:
    """将文档列表切分为文本块。

    使用 tiktoken 进行 token 计数，按滑动窗口方式切分。

    Args:
        documents: 文档列表
        chunk_size: 每个文本块的最大 token 数
        chunk_overlap: 相邻文本块的重叠 token 数
        encoding_name: tiktoken 编码名称

    Returns:
        TextUnit 列表
    """
    encoder = tiktoken.get_encoding(encoding_name)
    all_text_units: list[TextUnit] = []

    for doc in documents:
        chunks = _split_by_tokens(
            text=doc.raw_content,
            encoder=encoder,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for chunk_text, n_tokens in chunks:
            text_unit = TextUnit(
                id=str(uuid.uuid4()),
                text=chunk_text,
                n_tokens=n_tokens,
                document_ids=[doc.id],
            )
            all_text_units.append(text_unit)

        logger.info(
            f"文档 '{doc.title}' 切分为 {len(chunks)} 个文本块"
        )

    logger.info(f"共生成 {len(all_text_units)} 个文本块")
    return all_text_units


def _split_by_tokens(
    text: str,
    encoder: tiktoken.Encoding,
    chunk_size: int,
    chunk_overlap: int,
) -> list[tuple[str, int]]:
    """按 token 数切分文本，返回 (chunk_text, n_tokens) 列表。"""
    tokens = encoder.encode(text)
    total_tokens = len(tokens)

    if total_tokens <= chunk_size:
        return [(text, total_tokens)]

    chunks: list[tuple[str, int]] = []
    start = 0
    step = chunk_size - chunk_overlap

    while start < total_tokens:
        end = min(start + chunk_size, total_tokens)
        chunk_tokens = tokens[start:end]
        chunk_text = encoder.decode(chunk_tokens)
        chunks.append((chunk_text, len(chunk_tokens)))

        if end >= total_tokens:
            break
        start += step

    return chunks
