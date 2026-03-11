from abc import ABC, abstractmethod
from typing import Any

from common.llm.chat_model import LitellmChatModel


class BaseSearch(ABC):
    """
    Base class for all search engines in KGRAG.
    """

    def __init__(self, llm: LitellmChatModel, **kwargs: Any):
        self.llm = llm

    @abstractmethod
    def search(self, query: str, **kwargs: Any) -> Any:
        """
        Synchronous search.
        """
        pass

    @abstractmethod
    async def asearch(self, query: str, **kwargs: Any) -> Any:
        """
        Asynchronous search.
        """
        pass
