from typing import Protocol

from app.domain.model.search import SearchResults
from app.domain.model.tool_result import ToolResult


class SearchEngine(Protocol):
    """搜索引擎API接口协议"""

    async def invoke(
        self, query: str, date_range: str | None = None
    ) -> ToolResult[SearchResults]:
        """调用搜索引擎并传递query+date_range(日期检索范围))调用搜索引擎获取数据"""
        ...
