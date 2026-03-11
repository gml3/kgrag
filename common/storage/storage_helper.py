"""
Parquet 存储辅助

将数据模型对象序列化为 Parquet 文件。
"""

import logging
from dataclasses import asdict
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)


def save_parquet(data: list, filename: str, output_dir: str) -> str:
    """将 dataclass 列表保存为 Parquet 文件。

    Args:
        data: dataclass 对象列表
        filename: 输出文件名（如 'entities.parquet'）
        output_dir: 输出目录

    Returns:
        输出文件完整路径
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / filename

    if not data:
        logger.warning(f"空数据，跳过保存: {filename}")
        return str(file_path)

    # 将 dataclass 转为 dict 列表
    records = []
    for item in data:
        d = asdict(item)
        # 将 list/dict 字段转为 JSON 字符串（Parquet 不支持空 struct）
        for key, value in d.items():
            if isinstance(value, (list, dict)):
                import json
                d[key] = json.dumps(value, ensure_ascii=False)
        records.append(d)

    table = pa.Table.from_pylist(records)
    pq.write_table(table, file_path)

    logger.info(f"已保存 {len(data)} 条记录 → {file_path}")
    return str(file_path)
