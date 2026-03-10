"""
chat_model 基础连通性测试

测试 LitellmChatModel 能否正常调用 LLM API 并获得响应。
"""

from common.config.models.chat_model_config import ChatModelConfig
from common.llm.chat_model import LitellmChatModel


def test_chat_basic():
    """测试基本 chat 调用"""
    config = ChatModelConfig()
    model = LitellmChatModel(config)

    response = model.chat("你好，请用一句话介绍你自己。")

    # 验证返回结构
    assert response.output is not None
    assert isinstance(response.output.content, str)
    assert len(response.output.content) > 0
    assert len(response.history) == 2  # user + assistant

    print(f"✅ chat 返回: {response.output.content[:100]}")


def test_chat_stream():
    """测试流式调用"""
    config = ChatModelConfig()
    model = LitellmChatModel(config)

    chunks = list(model.chat_stream("用一句话说'你好'"))

    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert len(full_text) > 0

    print(f"✅ stream 返回 ({len(chunks)} chunks): {full_text[:100]}")


def test_chat_with_history():
    """测试多轮对话"""
    config = ChatModelConfig()
    model = LitellmChatModel(config)

    # 第一轮
    resp1 = model.chat("记住这个数字：42")
    assert len(resp1.history) == 2

    # 第二轮，传入历史
    resp2 = model.chat("我刚才让你记住的数字是多少？", history=resp1.history)
    assert len(resp2.history) == 4  # 2 轮 × 2 条消息
    assert "42" in resp2.output.content

    print(f"✅ 多轮对话: {resp2.output.content[:100]}")


if __name__ == "__main__":
    print("=" * 50)
    print("LitellmChatModel 连通性测试")
    print("=" * 50)

    test_chat_basic()
    test_chat_stream()
    test_chat_with_history()

    print("\n🎉 所有测试通过！")
