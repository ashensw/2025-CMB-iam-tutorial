from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MenuItem(BaseModel):
    """Pizza menu item model."""
    id: str = Field(..., description="Unique identifier for the pizza")
    name: str = Field(..., description="Name of the pizza")
    description: str = Field(..., description="Description of the pizza")
    price: float = Field(..., description="Price of the pizza")
    image_url: str = Field(..., description="URL of the pizza image")
    ingredients: List[str] = Field(..., description="List of ingredients")
    size_options: List[str] = Field(default=["Small", "Medium", "Large"], description="Available sizes")


class OrderItem(BaseModel):
    """Order item model."""
    pizza_id: str = Field(..., description="ID of the pizza being ordered")
    pizza_name: str = Field(..., description="Name of the pizza")
    quantity: int = Field(..., description="Quantity of pizzas")
    size: str = Field(default="Medium", description="Size of the pizza")
    special_instructions: Optional[str] = Field(None, description="Special instructions for the order")
    unit_price: float = Field(..., description="Price per pizza")
    total_price: float = Field(..., description="Total price for this item")


class Order(BaseModel):
    """Pizza order model."""
    order_id: str = Field(..., description="Unique order identifier")
    customer_id: str = Field(..., description="Customer identifier")
    customer_name: str = Field(..., description="Customer name")
    items: List[OrderItem] = Field(..., description="List of ordered items")
    subtotal: float = Field(..., description="Subtotal amount")
    tax: float = Field(..., description="Tax amount")
    delivery_fee: float = Field(default=2.99, description="Delivery fee")
    total: float = Field(..., description="Total order amount")
    status: str = Field(default="pending", description="Order status")
    created_at: datetime = Field(default_factory=datetime.now, description="Order creation timestamp")
    estimated_delivery: Optional[str] = Field(None, description="Estimated delivery time")


class ChatMessage(BaseModel):
    """Chat message model."""
    message: str = Field(..., description="User message")
    thread_id: Optional[str] = Field(None, description="Chat thread identifier")


class ChatResponse(BaseModel):
    """Chat response model."""
    chat_response: str = Field(..., description="Agent's text response")
    tool_response: Optional[dict] = Field(None, description="Tool execution results")
    message_states: Optional[List[str]] = Field(None, description="Current conversation states")


class AgentMessage(BaseModel):
    """Agent message model."""
    id: str = Field(..., description="Message identifier")
    response: ChatResponse = Field(..., description="Chat response")
    frontend_state: str = Field(..., description="Frontend state")
    message_states: List[str] = Field(..., description="Message states")


class MenuRequest(BaseModel):
    """Menu request model."""
    category: Optional[str] = Field(None, description="Pizza category filter")
    price_range: Optional[tuple] = Field(None, description="Price range filter")


class OrderRequest(BaseModel):
    """Order placement request model."""
    items: List[dict] = Field(..., description="List of items to order")
    customer_info: dict = Field(..., description="Customer information")
    delivery_address: Optional[str] = Field(None, description="Delivery address")
    special_instructions: Optional[str] = Field(None, description="Special order instructions")
