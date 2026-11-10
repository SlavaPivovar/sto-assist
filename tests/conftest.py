import pytest

from sto_assist.catalog import Catalog
from sto_assist.order import OrderStore
from sto_assist.tools import OrderSession


@pytest.fixture
def session(tmp_path):
    return OrderSession(Catalog.load(), OrderStore(tmp_path))


@pytest.fixture(autouse=True)
def nbu_offline(monkeypatch):
    """Тести не ходять у мережу: «банк недоступний», якщо тест не підставив свій курс."""
    from sto_assist import fx

    def offline():
        raise OSError("NBU недоступний у тестах")
    monkeypatch.setattr(fx.Rates, "_fetch_nbu", staticmethod(offline))
