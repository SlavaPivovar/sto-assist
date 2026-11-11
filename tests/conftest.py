from pathlib import Path

import pytest

from sto_assist.catalog import Catalog
from sto_assist.order import OrderStore
from sto_assist.tools import OrderSession


# Тести працюють на власному довіднику (ціни в $, роботи з обмеженням за моделями), а не на стартовому
# довіднику продукту: так вони не залежать від його наповнення й перевіряють код з іншою валютою.
TEST_CATALOG = Path(__file__).parent / "data" / "catalog.json"


@pytest.fixture(autouse=True)
def test_catalog(monkeypatch):
    monkeypatch.setattr("sto_assist.catalog.DEFAULT_CATALOG", TEST_CATALOG)
    monkeypatch.setattr("sto_assist.web.DEFAULT_CATALOG", TEST_CATALOG)


@pytest.fixture
def session(tmp_path):
    return OrderSession(Catalog.load(TEST_CATALOG), OrderStore(tmp_path))


@pytest.fixture(autouse=True)
def nbu_offline(monkeypatch):
    """Тести не ходять у мережу: «банк недоступний», якщо тест не підставив свій курс."""
    from sto_assist import fx

    def offline():
        raise OSError("NBU недоступний у тестах")
    monkeypatch.setattr(fx.Rates, "_fetch_nbu", staticmethod(offline))
