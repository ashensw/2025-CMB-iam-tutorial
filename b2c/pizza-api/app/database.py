"""
Database models and configuration for Pizza API
"""
import os
import json
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/pizzashack")
if DATABASE_URL.startswith("postgresql://") and "localhost" in DATABASE_URL:
    DATABASE_URL = "sqlite:///./pizza_shack.db"
    logger.info("Using SQLite for local development")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class MenuItem(Base):
    """Database model for menu items"""
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    image_url = Column(String(200))
    ingredients = Column(Text)  # JSON string
    size_options = Column(Text)  # JSON string
    available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Order(Base):
    """Database model for orders"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(String(100))  # From OBO token
    agent_id = Column(String(100))  # From agent token
    customer_info = Column(Text)  # JSON string
    items = Column(Text)  # JSON string
    total_amount = Column(Float)
    status = Column(String(20), default="pending")
    token_type = Column(String(20))  # "agent" or "obo"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


def init_database():
    """Create tables and populate initial data"""
    Base.metadata.create_all(bind=engine)
    
    # Populate menu data
    db = SessionLocal()
    try:
        if db.query(MenuItem).first():
            logger.info("Menu items already exist, skipping population")
            return
        
        menu_items = [
            {
                "name": "Tandoori Chicken",
                "description": "Classic supreme tender tandoori chicken, crisp bell peppers, onions, spiced tomato sauce",
                "price": 14.99,
                "category": "specialty",
                "image_url": "/images/tandoori_chicken.jpeg",
                "ingredients": ["Tandoori chicken", "Bell peppers", "Red onions", "Mozzarella cheese", "Spiced tomato sauce", "Indian herbs"],
                "size_options": ["Small ($12.99)", "Medium ($14.99)", "Large ($16.99)"]
            },
            {
                "name": "Spicy Jaffna Crab",
                "description": "Rich Jaffna-style crab curry, mozzarella, onions, fiery spice. An exotic coastal delight!",
                "price": 16.50,
                "category": "specialty",
                "image_url": "/images/spicy_jaffna_crab.jpeg",
                "ingredients": ["Jaffna crab curry", "Mozzarella cheese", "Red onions", "Chili flakes", "Curry leaves", "Coconut milk base"],
                "size_options": ["Small ($14.50)", "Medium ($16.50)", "Large ($18.50)"]
            },
            {
                "name": "Curry Chicken & Cashew",
                "description": "Sri Lankan chicken curry, roasted cashews, mozzarella. Unique flavor profile!",
                "price": 13.99,
                "category": "specialty",
                "image_url": "/images/curry_chicken_cashew.jpeg",
                "ingredients": ["Sri Lankan chicken curry", "Roasted cashews", "Mozzarella cheese", "Curry sauce", "Fresh coriander"],
                "size_options": ["Small ($11.99)", "Medium ($13.99)", "Large ($15.99)"]
            },
            {
                "name": "Spicy Paneer Veggie",
                "description": "Vegetarian kick! Marinated paneer, fresh vegetables, zesty spiced tomato base, mozzarella",
                "price": 13.50,
                "category": "vegetarian",
                "image_url": "/images/spicy_paneer_veggie.jpeg",
                "ingredients": ["Marinated paneer", "Bell peppers", "Red onions", "Tomatoes", "Mozzarella cheese", "Spiced tomato base"],
                "size_options": ["Small ($11.50)", "Medium ($13.50)", "Large ($15.50)"]
            },
            {
                "name": "Margherita Classic",
                "description": "Timeless classic with vibrant San Marzano tomato sauce, fresh mozzarella, and whole basil leaves",
                "price": 12.50,
                "category": "classic",
                "image_url": "/images/margherita_classic.jpeg",
                "ingredients": ["Fresh mozzarella", "San Marzano tomato sauce", "Whole basil leaves", "Extra virgin olive oil", "Sea salt"],
                "size_options": ["Small ($10.50)", "Medium ($12.50)", "Large ($14.50)"]
            },
            {
                "name": "Four Cheese Fusion",
                "description": "A cheese lover's dream with mozzarella, sharp cheddar, Parmesan, and creamy ricotta.",
                "price": 13.25,
                "category": "premium",
                "image_url": "/images/four_cheese_fusion.jpeg",
                "ingredients": ["Mozzarella", "Sharp cheddar", "Parmesan", "Creamy ricotta", "Artisan crust", "Olive oil"],
                "size_options": ["Small ($11.25)", "Medium ($13.25)", "Large ($15.25)"]
            },
            {
                "name": "Hot Butter Prawn",
                "description": "Juicy prawns in signature hot butter sauce with mozzarella and spring onions.",
                "price": 15.50,
                "category": "specialty",
                "image_url": "/images/hot_butter_prawn.jpeg",
                "ingredients": ["Juicy prawns", "Hot butter sauce", "Mozzarella cheese", "Spring onions", "Garlic", "Chili flakes"],
                "size_options": ["Small ($13.50)", "Medium ($15.50)", "Large ($17.50)"]
            },
            {
                "name": "Masala Potato & Pea",
                "description": "Comforting vegetarian choice! Spiced potatoes, green peas, Indian spices, mozzarella",
                "price": 12.99,
                "category": "vegetarian",
                "image_url": "/images/masala_potato_pea.jpeg",
                "ingredients": ["Spiced potatoes", "Green peas", "Mozzarella cheese", "Masala spices", "Fresh coriander", "Cumin"],
                "size_options": ["Small ($10.99)", "Medium ($12.99)", "Large ($14.99)"]
            }
        ]
        
        for item_data in menu_items:
            menu_item = MenuItem(
                name=item_data["name"],
                description=item_data["description"],
                price=item_data["price"],
                category=item_data["category"],
                image_url=item_data["image_url"],
                ingredients=json.dumps(item_data["ingredients"]),
                size_options=json.dumps(item_data["size_options"])
            )
            db.add(menu_item)
        
        db.commit()
        logger.info("Menu items populated successfully")
        
    except Exception as e:
        logger.error(f"Error populating menu: {e}")
        db.rollback()
    finally:
        db.close()