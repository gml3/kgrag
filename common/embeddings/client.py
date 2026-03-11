import logging
import requests
from typing import List, Tuple, Dict, Any

from common.config.models.embedding_model_config import EmbeddingModelConfig

logger = logging.getLogger(__name__)

def convert_text_to_vec(
    text_list: List[str],
    embedding_config: EmbeddingModelConfig,
) -> Tuple[List[List[float]], List[Dict]]:
    """调用 Embedding 模型服务获取稠密和稀疏向量。

    Args:
        text_list: 文本列表
        embedding_config: Embedding 配置

    Returns:
        (dense_vectors, sparse_vectors)
    """
    payload = {"sentences": text_list}
    response = requests.post(
        embedding_config.api_base,
        headers=embedding_config.headers,
        json=payload,
    )
    response.raise_for_status()

    resp_data = response.json().get("data", [])
    data_list = resp_data["data"] if isinstance(resp_data, dict) and "data" in resp_data else resp_data

    dense_vectors = [item["dense_embedding"] for item in data_list]
    sparse_vectors = [item.get("sparse_embedding", {}) for item in data_list]

    return dense_vectors, sparse_vectors
