"""
Pydantic models for Pizza API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class MenuItemResponse(BaseModel):
    """Response model for menu items"""
    id: int
    name: str
    description: Optional[str]
    price: float
    category: str
    image_url: Optional[str]
    ingredients: List[str]
    size_options: List[str]
    available: bool


class OrderItem(BaseModel):
    """Order item model for creating orders"""
    menu_item_id: int
    quantity: int = Field(gt=0)
    size: str = "medium"
    special_instructions: Optional[str] = None


class CreateOrderRequest(BaseModel):
    """Request model for creating new orders"""
    items: List[OrderItem]
    customer_info: Optional[Dict[str, Any]] = None


class OrderResponse(BaseModel):
    """Response model for order information"""
    id: int
    order_id: str
    user_id: Optional[str]
    agent_id: Optional[str]
    items: List[Dict[str, Any]]
    total_amount: float
    status: str
    token_type: str
    created_at: datetime


class Actor(BaseModel):
    """Actor information for OBO tokens"""
    sub: Optional[str] = None


class TokenInfo(BaseModel):
    """Token information extracted from JWT"""
    token_type: str  # "user" or "obo"
    user_id: Optional[str]
    agent_id: Optional[str]
    raw_token: str  # Original token for passing to external services
    scopes: List[str] = []  # Token scopes for authorization


class TokenData(BaseModel):
    """Token data compatible with hotel API patterns"""
    sub: Optional[str] = None
    act: Actor = Actor()
    scopes: List[str] = []


class ApiInfo(BaseModel):
    """API information response"""
    name: str
    version: str
    description: str
    docs_url: str
    status_url: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str


class SystemStatusResponse(BaseModel):
    """System status response"""
    status: str
    database: str
    services: Dict[str, str]
    uptime: str
    timestamp: str


class TokenInfoResponse(BaseModel):
    """Token information endpoint response"""
    user_id: Optional[str]
    token_type: str
    agent_id: Optional[str]


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    status_code: int
    timestamp: str