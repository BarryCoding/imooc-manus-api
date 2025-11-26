from fastapi.testclient import TestClient
from pytest import fixture

from app.main import app


@fixture(scope="session")
def client() -> TestClient:
    """
    创建一个可供所有测试用例使用的 TestClient 客户端
    scope="session" 表示这个fixture 在整个测试用例只会实例一次 这样可以提高测试效率
    :return: TestClient
    """
    with TestClient(app) as c:
        yield c
