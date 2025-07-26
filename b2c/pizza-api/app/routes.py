"""
API routes for Pizza Shack API
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from .schemas import (
    MenuItemResponse, CreateOrderRequest, OrderResponse, 
    TokenInfo, TokenData, ApiInfo, HealthResponse, SystemStatusResponse,
    TokenInfoResponse
)
from .database import MenuItem, Order
from .dependencies import get_db, validate_token, simple_validate_token, log_request_headers, security

logger = logging.getLogger(__name__)

# Create router instances
main_router = APIRouter()
api_router = APIRouter(prefix="/api")


def log_request_details(request: Request, token_data: TokenData, extra_info: dict = None):
    """Enhanced logging function with structured information"""
    endpoint = request.url.path
    method = request.method
    sub = token_data.sub
    act = token_data.act.sub
    
    # Get client IP
    client_ip = request.client.host if request.client else 'N/A'
    
    # Build log message
    log_data = {
        "method": method,
        "endpoint": endpoint,
        "client_ip": client_ip,
        "user_id": sub,
        "actor": act,
    }
    
    # Add extra information if provided
    if extra_info:
        log_data.update(extra_info)
    
    # Create structured log message
    log_message = " | ".join([
        f"{method} {endpoint}",
        f"sub: {sub}",
        f"act: {act}",
    ])
    
    # Add extra info to message if provided
    if extra_info:
        extra_parts = []
        for key, value in extra_info.items():
            extra_parts.append(f"{key}: {value}")
        if extra_parts:
            log_message += " | " + " | ".join(extra_parts)
    
    logger.info(log_message)


# Main routes (no /api prefix)
@main_router.get("/", response_model=ApiInfo)
def root():
    """API information endpoint"""
    return ApiInfo(
        name="Pizza Shack API",
        version="1.0.0",
        description="Pizza ordering API with IETF Agent Authentication",
        docs_url="/docs",
        status_url="/api/system/status"
    )


@main_router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy", 
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# API routes (with /api prefix)
@api_router.get("/token-info", response_model=TokenInfoResponse)
def token_info_endpoint(token_info: TokenInfo = Depends(simple_validate_token)):
    """Get token information for debugging - no scope validation"""
    return TokenInfoResponse(
        user_id=token_info.user_id,
        token_type=token_info.token_type,
        agent_id=token_info.agent_id
    )


@api_router.get("/menu", response_model=List[MenuItemResponse])
def get_menu(
    request: Request,
    category: Optional[str] = None,
    price_range: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get pizza menu with optional filtering (now with JWT logging for testing)"""
    
    # Basic logging to confirm this function is called
    logger.info("🍕 [MENU] Menu endpoint called with authentication")
    logger.info(f"🍕 [MENU] Request from: {request.client.host if request.client else 'Unknown'}")
    
    # Log request headers for JWT testing
    log_request_headers(request, credentials)
    
    query = db.query(MenuItem).filter(MenuItem.available == True)
    
    if category:
        query = query.filter(MenuItem.category == category.lower())
    
    if price_range:
        if price_range.lower() == "budget":
            query = query.filter(MenuItem.price <= 12.00)
        elif price_range.lower() == "mid-range":
            query = query.filter(MenuItem.price > 12.00, MenuItem.price <= 14.00)
        elif price_range.lower() == "premium":
            query = query.filter(MenuItem.price > 14.00)
    
    menu_items = query.all()
    
    result = []
    for item in menu_items:
        result.append(MenuItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            category=item.category,
            image_url=item.image_url,
            ingredients=item.ingredients if item.ingredients else [],
            size_options=item.size_options if item.size_options else [],
            available=item.available
        ))
    
    return result


@api_router.get("/system/status", response_model=SystemStatusResponse)
def system_status():
    """System status endpoint - no authentication required"""
    return SystemStatusResponse(
        status="operational",
        database="connected",
        services={
            "order_processing": "active", 
            "menu_service": "active"
        },
        uptime="running",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@api_router.post("/orders", response_model=OrderResponse)
def create_order(
    request: Request,
    order_request: CreateOrderRequest,
    token_data: TokenData = Security(validate_token, scopes=["order:write"]),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new order - requires order:write scope"""
    
    # Log request headers for debugging
    log_request_headers(request, credentials)
    log_request_details(request, token_data)
    
    if not token_data.sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User context required to place orders"
        )
    
    total_amount = 0.0
    order_items = []
    
    for item in order_request.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item {item.menu_item_id} not found"
            )
        
        if not menu_item.available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu item {menu_item.name} is not available"
            )
        
        item_total = menu_item.price * item.quantity
        total_amount += item_total
        
        order_items.append({
            "menu_item_id": item.menu_item_id,
            "name": menu_item.name,
            "quantity": item.quantity,
            "size": item.size,
            "unit_price": menu_item.price,
            "total_price": item_total,
            "special_instructions": item.special_instructions
        })
    
    order_id = f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{len(order_items)}"
    
    # Determine token type based on presence of agent
    token_type = "obo" if token_data.act.sub else "user"
    
    new_order = Order(
        order_id=order_id,
        user_id=token_data.sub,
        agent_id=token_data.act.sub,
        customer_info=json.dumps(order_request.customer_info or {}),
        items=json.dumps(order_items),
        total_amount=total_amount,
        status="confirmed",
        token_type=token_type
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    creator = f"agent: {token_data.act.sub}" if token_data.act.sub else "user"
    logger.info(f"Order created: {order_id} for user: {token_data.sub} via {creator}")
    
    return OrderResponse(
        id=new_order.id,
        order_id=new_order.order_id,
        user_id=new_order.user_id,
        agent_id=new_order.agent_id,
        items=json.loads(new_order.items),
        total_amount=new_order.total_amount,
        status=new_order.status,
        token_type=new_order.token_type,
        created_at=new_order.created_at
    )


@api_router.get("/orders", response_model=List[OrderResponse])
def get_user_orders(
    request: Request,
    token_data: TokenData = Security(validate_token, scopes=["order:read"]),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get orders for the authenticated user - requires order:read scope"""
    
    # Log request headers for debugging
    log_request_headers(request, credentials)
    log_request_details(request, token_data)
    
    user_id = token_data.sub
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to determine user ID from token"
        )
    
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    
    result = []
    for order in orders:
        result.append(OrderResponse(
            id=order.id,
            order_id=order.order_id,
            user_id=order.user_id,
            agent_id=order.agent_id,
            items=json.loads(order.items),
            total_amount=order.total_amount,
            status=order.status,
            token_type=order.token_type,
            created_at=order.created_at
        ))
    
    return result


@api_router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    request: Request,
    order_id: str,
    token_data: TokenData = Security(validate_token, scopes=["order:read"]),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get specific order - user can only access their own orders - requires order:read scope"""
    
    # Log request headers for debugging
    log_request_headers(request, credentials)
    log_request_details(request, token_data)
    
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != token_data.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own orders"
        )
    
    return OrderResponse(
        id=order.id,
        order_id=order.order_id,
        user_id=order.user_id,
        agent_id=order.agent_id,
        items=json.loads(order.items),
        total_amount=order.total_amount,
        status=order.status,
        token_type=order.token_type,
        created_at=order.created_at
    )


# Admin endpoint removed - not used by pizza-shack frontend
# If needed later, can be re-added with order:admin scope