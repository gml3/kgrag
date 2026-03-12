"""
Step 1: 文档加载

从输入目录读取原始文档，生成 Document 列表。
"""

import logging
import uuid
from pathlib import Path

from common.config.models.document_loader_config import DocumentLoaderConfig
from common.models.document import Document

logger = logging.getLogger(__name__)


def load_documents(config: DocumentLoaderConfig) -> list[Document]:
    """从输入目录加载所有支持格式的文档。

    Args:
        config: DocumentLoaderConfig 配置

    Returns:
        Document 列表
    """
    input_path = Path(config.input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"输入目录不存在: {config.input_dir}")

    supported_extensions = config.supported_extensions
    documents: list[Document] = []

    for file_path in sorted(input_path.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                content = _read_file(file_path)
                doc = Document(
                    id=str(uuid.uuid4()),
                    title=file_path.stem,
                    raw_content=content,
                    file_path=str(file_path),
                    file_type=file_path.suffix.lstrip("."),
                )
                documents.append(doc)
                logger.info(f"已加载文档: {file_path.name} ({len(content)} 字符)")
            except Exception as e:
                logger.warning(f"跳过文件 {file_path.name}: {e}")

    logger.info(f"共加载 {len(documents)} 个文档")
    return documents


def _read_file(file_path: Path) -> str:
    """读取文件内容。"""
    suffix = file_path.suffix.lower()

    if suffix == ".txt":
        return file_path.read_text(encoding="utf-8")

    elif suffix == ".csv":
        # CSV: 将所有行拼接为文本
        return file_path.read_text(encoding="utf-8")

    elif suffix == ".json":
        return file_path.read_text(encoding="utf-8")

    else:
        raise ValueError(f"不支持的文件格式: {suffix}")



if __name__ == "__main__":
    print(load_documents("./data/input"))