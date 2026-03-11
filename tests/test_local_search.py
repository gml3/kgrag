import pandas as pd
import sys
from unittest.mock import MagicMock
sys.modules['common.config.models.chat_model_config'] = MagicMock()
sys.modules['litellm'] = MagicMock()

# 先行 mock Milvus 库及请求库以防止后续 LocalSearch 导入报错
sys.modules['pymilvus'] = MagicMock()
mock_milvus_client_class = MagicMock()
sys.modules['pymilvus'].MilvusClient = mock_milvus_client_class
sys.modules['common.embeddings.client'] = MagicMock()

from chat.context_builder import ContextBuilder
from chat.search.local_search import LocalSearch
from common.llm.base import LitellmModelResponse, LitellmModelOutput

# Dummy LLM for testing
class DummyLLM:
    def chat(self, prompt: str, history=None):
        return LitellmModelResponse(
            output=LitellmModelOutput(content=f"Mock LLM Response for prompt length {len(prompt)}"),
            parsed_response=None,
            history=history or []
        )

def test_context_builder():
    entities_data = {
        'id': ['e1', 'e2'],
        'title': ['Alice', 'Bob'],
        'type': ['PERSON', 'PERSON'],
        'description': ['A person named Alice', 'A person named Bob'],
        'community_ids': [['c1'], ['c1']],
        'text_unit_ids': [['t1'], ['t1', 't2']]
    }
    
    relationships_data = {
        'source': ['e1'],
        'target': ['e2'],
        'description': ['Alice knows Bob']
    }
    
    text_units_data = {
        'id': ['t1', 't2'],
        'text': ['Alice and Bob went to the park.', 'Bob bought a coffee.']
    }
    
    community_reports_data = {
        'community_id': ['c1'],
        'title': ['Park Visitors'],
        'summary': ['A community of people who visit the park.']
    }
    
    eb = ContextBuilder(
        pd.DataFrame(entities_data),
        pd.DataFrame(relationships_data),
        pd.DataFrame(text_units_data),
        pd.DataFrame(community_reports_data)
    )
    
    context = eb.build_context(['Alice', 'Bob'], max_tokens=12000)
    print("--- Context Output ---")
    print(context)
    
    assert "Park Visitors" in context
    assert "Alice knows Bob" in context
    assert "Alice and Bob went to the park." in context

def test_local_search():
    from common.config.models.embedding_model_config import EmbeddingModelConfig
    from common.config.models.milvus_config import MilvusConfig
    
    # Mock MilvusClient search
    sys.modules['pymilvus'] = MagicMock()
    mock_milvus_client_class = MagicMock()
    mock_client_instance = mock_milvus_client_class.return_value
    mock_client_instance.search.return_value = [[{"id": "e1", "entity_title": "Alice"}, {"id": "e2", "entity_title": "Bob"}]]
    sys.modules['pymilvus'].MilvusClient = mock_milvus_client_class
    
    # Mock convert_text_to_vec
    mock_convert = MagicMock(return_value=([[1.0, 2.0]], []))
    sys.modules['common.embeddings.client'] = MagicMock()
    sys.modules['common.embeddings.client'].convert_text_to_vec = mock_convert
    
    eb = ContextBuilder(
        pd.DataFrame({'id': ['e1', 'e2'], 'title': ['Alice', 'Bob'], 'type':['P','P']}),
        pd.DataFrame(columns=['source', 'target', 'description']),
        pd.DataFrame(columns=['id', 'text']),
        pd.DataFrame(columns=['community_id', 'title', 'summary'])
    )
    
    # 重新导入被 Mock 的依赖后的 Search 模块
    import importlib
    import chat.search.local_search
    importlib.reload(chat.search.local_search)
    from chat.search.local_search import LocalSearch
    
    search_engine = LocalSearch(
        llm=DummyLLM(),
        context_builder=eb,
        embedding_config=EmbeddingModelConfig(),
        milvus_config=MilvusConfig()
    )
    
    res = search_engine.search("Who are Alice and Bob?")
    print("--- Search Result ---")
    print(res.output.content)
    assert res is not None

if __name__ == "__main__":
    test_context_builder()
    test_local_search()
    print("All tests passed!")
