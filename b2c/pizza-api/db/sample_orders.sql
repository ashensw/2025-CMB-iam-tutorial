-- Sample order data for testing "My Orders" functionality

INSERT INTO orders (
  order_id, user_id, agent_id, customer_info, items, total_amount,
  status, token_type, created_at, updated_at
) VALUES

-- Demo user orders
('ORD-20250721143001-2', 'aedc826d-26f9-42b5-871c-07c5148884ea', NULL, 
 '{"name": "John Doe", "email": "john.doe@example.com", "phone": "+1-555-0123"}',
 '[{"menu_item_id": 5, "name": "Margherita Classic", "quantity": 2, "size": "medium", "unit_price": 12.50, "total_price": 25.00, "special_instructions": "Extra basil please"}]',
 25.00, 'confirmed', 'user', '2025-07-21 14:30:01', '2025-07-21 14:30:01'),

('ORD-20250721135502-3', 'aedc826d-26f9-42b5-871c-07c5148884ea', 'pizza-agent-demo',
 '{"name": "John Doe", "email": "john.doe@example.com", "phone": "+1-555-0123"}',
 '[{"menu_item_id": 6, "name": "Four Cheese Fusion", "quantity": 1, "size": "large", "unit_price": 13.25, "total_price": 13.25}, {"menu_item_id": 4, "name": "Spicy Paneer Veggie", "quantity": 1, "size": "medium", "unit_price": 13.50, "total_price": 13.50}]',
 26.75, 'pending', 'obo', '2025-07-21 13:55:02', '2025-07-21 14:15:02'),

('ORD-20250721120003-1', '846884e9-ea64-4038-80aa-821b09fd1840', NULL,
 '{"name": "John Doe", "email": "john.doe@example.com", "phone": "+1-555-0123"}',
 '[{"menu_item_id": 1, "name": "Tandoori Chicken", "quantity": 1, "size": "medium", "unit_price": 14.99, "total_price": 14.99}]',
 14.99, 'delivered', 'user', '2025-07-21 12:00:03', '2025-07-21 12:45:03'),

-- Agent-placed order
('ORD-20250721164504-4', 'aedc826d-26f9-42b5-871c-07c5148884ea', 'pizza-agent-demo',
 '{"name": "Jane Smith", "email": "jane.smith@company.com", "phone": "+1-555-0456", "company": "Tech Corp"}',
 '[{"menu_item_id": 5, "name": "Margherita Classic", "quantity": 3, "size": "large", "unit_price": 12.50, "total_price": 37.50}, {"menu_item_id": 3, "name": "Curry Chicken & Cashew", "quantity": 2, "size": "medium", "unit_price": 13.99, "total_price": 27.98}]',
 65.48, 'confirmed', 'obo', '2025-07-21 16:45:04', '2025-07-21 16:45:04'),

-- Another user's orders
('ORD-20250721100505-2', '846884e9-ea64-4038-80aa-821b09fd1840', 'pizza-agent-demo',
 '{"name": "Alice Johnson", "email": "alice.johnson@email.com", "phone": "+1-555-0789"}',
 '[{"menu_item_id": 8, "name": "Masala Potato & Pea", "quantity": 2, "size": "small", "unit_price": 12.99, "total_price": 25.98, "special_instructions": "Extra coriander please"}]',
 25.98, 'confirmed', 'obo', '2025-07-21 10:05:05', '2025-07-21 10:25:05'),

-- Recent order
('ORD-20250721173006-1', 'aedc826d-26f9-42b5-871c-07c5148884ea', NULL,
 '{"name": "John Doe", "email": "john.doe@example.com", "phone": "+1-555-0123"}',
 '[{"menu_item_id": 6, "name": "Four Cheese Fusion", "quantity": 1, "size": "medium", "unit_price": 13.25, "total_price": 13.25}, {"menu_item_id": 2, "name": "Spicy Jaffna Crab", "quantity": 1, "size": "small", "unit_price": 16.50, "total_price": 16.50}]',
 29.75, 'pending', 'user', '2025-07-21 17:30:06', '2025-07-21 17:30:06')

ON CONFLICT (order_id) DO NOTHING;