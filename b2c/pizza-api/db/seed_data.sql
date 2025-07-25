-- Pizza Shack Initial Data
-- Populates menu_items table with current Sri Lankan-inspired pizza menu

INSERT INTO menu_items (
  name, 
  description, 
  price, 
  category, 
  image_url, 
  ingredients, 
  size_options, 
  available
) VALUES
(
  'Tandoori Chicken', 
  'Classic supreme tender tandoori chicken, crisp bell peppers, onions, spiced tomato sauce', 
  14.99, 
  'chicken', 
  '/images/tandoori_chicken.jpeg', 
  '["Tandoori chicken", "Bell peppers", "Red onions", "Mozzarella cheese", "Spiced tomato sauce", "Indian spices"]', 
  '["Small ($12.99)", "Medium ($14.99)", "Large ($16.99)"]', 
  TRUE
),
(
  'Spicy Jaffna Crab', 
  'Rich Jaffna-style crab curry, mozzarella, onions, fiery spice. An exotic coastal delight!', 
  16.50, 
  'seafood', 
  '/images/spicy_jaffna_crab.jpeg', 
  '["Jaffna crab curry", "Mozzarella cheese", "Red onions", "Chili flakes", "Coconut cream", "Sri Lankan spices"]', 
  '["Small ($14.50)", "Medium ($16.50)", "Large ($18.50)"]', 
  TRUE
),
(
  'Curry Chicken & Cashew', 
  'Sri Lankan chicken curry, roasted cashews, mozzarella. Unique flavor profile!', 
  13.99, 
  'chicken', 
  '/images/curry_chicken_cashew.jpeg', 
  '["Sri Lankan chicken curry", "Roasted cashews", "Mozzarella cheese", "Curry leaves", "Coconut milk", "Turmeric"]', 
  '["Small ($11.99)", "Medium ($13.99)", "Large ($15.99)"]', 
  TRUE
),
(
  'Spicy Paneer Veggie', 
  'Vegetarian kick! Marinated paneer, fresh vegetables, zesty spiced tomato base, mozzarella', 
  13.50, 
  'vegetarian', 
  '/images/spicy_paneer_veggie.jpeg', 
  '["Marinated paneer", "Bell peppers", "Red onions", "Mozzarella cheese", "Spiced tomato sauce", "Indian herbs"]', 
  '["Small ($11.50)", "Medium ($13.50)", "Large ($15.50)"]', 
  TRUE
),
(
  'Margherita Classic', 
  'Timeless classic with vibrant San Marzano tomato sauce, fresh mozzarella, and whole basil leaves', 
  12.50, 
  'classic', 
  '/images/margherita_classic.jpeg', 
  '["Fresh mozzarella", "San Marzano tomato sauce", "Fresh basil leaves", "Extra virgin olive oil", "Sea salt"]', 
  '["Small ($10.50)", "Medium ($12.50)", "Large ($14.50)"]', 
  TRUE
),
(
  'Four Cheese Fusion', 
  'A cheese lover''s dream with mozzarella, sharp cheddar, Parmesan, and creamy ricotta.', 
  13.25, 
  'cheese', 
  '/images/four_cheese_fusion.jpeg', 
  '["Mozzarella", "Sharp cheddar", "Parmesan", "Ricotta", "White sauce base", "Black pepper"]', 
  '["Small ($11.25)", "Medium ($13.25)", "Large ($15.25)"]', 
  TRUE
),
(
  'Hot Butter Prawn', 
  'Juicy prawns in signature hot butter sauce with mozzarella and spring onions.', 
  15.50, 
  'seafood', 
  '/images/hot_butter_prawn.jpeg', 
  '["Fresh prawns", "Hot butter sauce", "Mozzarella cheese", "Spring onions", "Garlic", "Chili flakes"]', 
  '["Small ($13.50)", "Medium ($15.50)", "Large ($17.50)"]', 
  TRUE
),
(
  'Masala Potato & Pea', 
  'Comforting vegetarian choice! Spiced potatoes, green peas, Indian spices, mozzarella', 
  12.99, 
  'vegetarian', 
  '/images/masala_potato_pea.jpeg', 
  '["Spiced potatoes", "Green peas", "Mozzarella cheese", "Indian masala spices", "Tomato base", "Fresh coriander"]', 
  '["Small ($10.99)", "Medium ($12.99)", "Large ($14.99)"]', 
  TRUE
)
ON CONFLICT (name) DO NOTHING;
