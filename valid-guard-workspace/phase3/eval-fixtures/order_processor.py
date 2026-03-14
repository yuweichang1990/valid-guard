"""Order processing module with intentional coverage gaps for brownfield eval."""

from enum import Enum
from decimal import Decimal
from datetime import datetime, timedelta


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class InsufficientStockError(Exception):
    pass


class InvalidTransitionError(Exception):
    pass


class OrderProcessor:
    TAX_RATE = Decimal("0.08")
    FREE_SHIPPING_THRESHOLD = Decimal("50.00")
    SHIPPING_FEE = Decimal("5.99")
    MAX_ITEMS_PER_ORDER = 100
    REFUND_WINDOW_DAYS = 30

    def __init__(self, inventory: dict[str, int], pricing: dict[str, Decimal]):
        self.inventory = inventory
        self.pricing = pricing
        self.orders: dict[str, dict] = {}

    def create_order(self, order_id: str, items: dict[str, int]) -> dict:
        if not items:
            raise ValueError("Order must contain at least one item")

        total_items = sum(items.values())
        if total_items > self.MAX_ITEMS_PER_ORDER:
            raise ValueError(f"Cannot order more than {self.MAX_ITEMS_PER_ORDER} items")

        for item, qty in items.items():
            if qty <= 0:
                raise ValueError(f"Quantity must be positive for {item}")
            if item not in self.pricing:
                raise ValueError(f"Unknown item: {item}")
            if item not in self.inventory or self.inventory[item] < qty:
                raise InsufficientStockError(f"Not enough stock for {item}")

        subtotal = sum(
            self.pricing[item] * qty for item, qty in items.items()
        )
        tax = subtotal * self.TAX_RATE
        shipping = (
            Decimal("0") if subtotal >= self.FREE_SHIPPING_THRESHOLD
            else self.SHIPPING_FEE
        )
        total = subtotal + tax + shipping

        # Reserve inventory
        for item, qty in items.items():
            self.inventory[item] -= qty

        order = {
            "id": order_id,
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "shipping": shipping,
            "total": total,
            "status": OrderStatus.PENDING,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        self.orders[order_id] = order
        return order

    def transition_status(self, order_id: str, new_status: OrderStatus) -> dict:
        if order_id not in self.orders:
            raise KeyError(f"Order {order_id} not found")

        order = self.orders[order_id]
        current = order["status"]

        valid_transitions = {
            OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
            OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
            OrderStatus.PROCESSING: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
            OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
            OrderStatus.DELIVERED: {OrderStatus.REFUNDED},
            OrderStatus.CANCELLED: set(),
            OrderStatus.REFUNDED: set(),
        }

        if new_status not in valid_transitions.get(current, set()):
            raise InvalidTransitionError(
                f"Cannot transition from {current.value} to {new_status.value}"
            )

        order["status"] = new_status
        order["updated_at"] = datetime.now()

        # Restore inventory on cancellation
        if new_status == OrderStatus.CANCELLED:
            for item, qty in order["items"].items():
                self.inventory[item] = self.inventory.get(item, 0) + qty

        return order

    def request_refund(self, order_id: str) -> dict:
        if order_id not in self.orders:
            raise KeyError(f"Order {order_id} not found")

        order = self.orders[order_id]

        if order["status"] != OrderStatus.DELIVERED:
            raise InvalidTransitionError("Can only refund delivered orders")

        days_since = (datetime.now() - order["created_at"]).days
        if days_since > self.REFUND_WINDOW_DAYS:
            raise ValueError(
                f"Refund window expired ({days_since} days > {self.REFUND_WINDOW_DAYS})"
            )

        order["status"] = OrderStatus.REFUNDED
        order["updated_at"] = datetime.now()
        order["refund_amount"] = order["total"]

        # Restore inventory
        for item, qty in order["items"].items():
            self.inventory[item] = self.inventory.get(item, 0) + qty

        return order

    def apply_discount(self, order_id: str, discount_percent: Decimal) -> dict:
        if order_id not in self.orders:
            raise KeyError(f"Order {order_id} not found")

        if not (Decimal("0") < discount_percent <= Decimal("100")):
            raise ValueError("Discount must be between 0 (exclusive) and 100 (inclusive)")

        order = self.orders[order_id]
        if order["status"] != OrderStatus.PENDING:
            raise InvalidTransitionError("Can only apply discount to pending orders")

        discount = order["subtotal"] * discount_percent / Decimal("100")
        new_subtotal = order["subtotal"] - discount
        new_tax = new_subtotal * self.TAX_RATE
        new_shipping = (
            Decimal("0") if new_subtotal >= self.FREE_SHIPPING_THRESHOLD
            else self.SHIPPING_FEE
        )

        order["discount"] = discount
        order["subtotal"] = new_subtotal
        order["tax"] = new_tax
        order["shipping"] = new_shipping
        order["total"] = new_subtotal + new_tax + new_shipping
        order["updated_at"] = datetime.now()

        return order
