"""Existing test file with intentional gaps for brownfield eval.
These tests have decent coverage but miss critical scenarios."""

import pytest
from decimal import Decimal
from order_processor import OrderProcessor, OrderStatus, InsufficientStockError


@pytest.fixture
def processor():
    inventory = {"widget": 10, "gadget": 5, "gizmo": 20}
    pricing = {
        "widget": Decimal("10.00"),
        "gadget": Decimal("25.00"),
        "gizmo": Decimal("3.50"),
    }
    return OrderProcessor(inventory, pricing)


class TestCreateOrder:
    def test_create_simple_order(self, processor):
        order = processor.create_order("ORD-1", {"widget": 2})
        assert order["subtotal"] == Decimal("20.00")
        assert order["status"] == OrderStatus.PENDING

    def test_create_order_with_multiple_items(self, processor):
        order = processor.create_order("ORD-2", {"widget": 1, "gadget": 1})
        assert order["subtotal"] == Decimal("35.00")

    def test_create_order_empty_items_raises(self, processor):
        with pytest.raises(ValueError):
            processor.create_order("ORD-3", {})

    def test_insufficient_stock_raises(self, processor):
        with pytest.raises(InsufficientStockError):
            processor.create_order("ORD-4", {"widget": 999})


class TestTransitionStatus:
    def test_pending_to_confirmed(self, processor):
        processor.create_order("ORD-1", {"widget": 1})
        order = processor.transition_status("ORD-1", OrderStatus.CONFIRMED)
        assert order["status"] == OrderStatus.CONFIRMED

    def test_confirmed_to_shipped_raises(self, processor):
        processor.create_order("ORD-1", {"widget": 1})
        processor.transition_status("ORD-1", OrderStatus.CONFIRMED)
        with pytest.raises(Exception):
            processor.transition_status("ORD-1", OrderStatus.SHIPPED)


class TestDiscount:
    def test_apply_10_percent_discount(self, processor):
        processor.create_order("ORD-1", {"gadget": 3})
        order = processor.apply_discount("ORD-1", Decimal("10"))
        assert order["discount"] == Decimal("7.500")
