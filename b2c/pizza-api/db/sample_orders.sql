-- Sample order data for testing "My Orders" functionality
-- This creates realistic orders with different statuses and users

INSERT INTO orders (order_id, user_id, agent_id, customer_info, items, total_amount, status, token_type, created_at, updated_at) VALUES

-- Demo user orders (for testing without authentication)
('ORD-20250721143001-2', 'demo-user-123', 'pizza-agent-demo', 
 '{"name": "John Doe", "email": "john.doe@example.com", "phone": "+1-555-0123"}',
 '[{"menu_item_id": 1, "name": "Margherita Classic", "quantity": 2, "size": "medium", "unit_price": 10.99, "total_price": 21.98, "special_instructions": "Extra basil please"}]',
 21.98, 'confirmed', 'obo', '2025-07-21 14:30:01', '2025-07-21 14:30:01'),

('ORD-20250721135502-3', 'demo-user-123', 'pizza-agent-demo',
 '{"name": "John Doe", "email": "john.doe@example.com", "phone": "+1-555-0123"}',
 '[{"menu_item_id": 2, "name": "Four Cheese Deluxe", "quantity": 1, "size": "large", "unit_price": 12.99, "total_price": 12.99}, {"menu_item_id": 5, "name": "Veggie Garden", "quantity": 1, "size": "medium", "unit_price": 11.99, "total_price": 11.99}]',
 24.98, 'preparing', 'obo', '2025-07-21 13:55:02', '2025-07-21 14:15:02'),

('ORD-20250721120003-1', 'demo-user-123', 'pizza-agent-demo',
 '{"name": "John Doe", "email": "john.doe@example.com", "phone": "+1-555-0123"}',
 '[{"menu_item_id": 4, "name": "Pepperoni Supreme", "quantity": 1, "size": "medium", "unit_price": 13.99, "total_price": 13.99}]',
 13.99, 'delivered', 'obo', '2025-07-21 12:00:03', '2025-07-21 12:45:03'),

-- Agent-placed orders (for testing agent functionality)
('ORD-20250721164504-4', 'jane.smith@company.com', 'pizza-agent-corporate',
 '{"name": "Jane Smith", "email": "jane.smith@company.com", "phone": "+1-555-0456", "company": "Tech Corp"}',
 '[{"menu_item_id": 1, "name": "Margherita Classic", "quantity": 3, "size": "large", "unit_price": 10.99, "total_price": 32.97}, {"menu_item_id": 3, "name": "Marinara Special", "quantity": 2, "size": "medium", "unit_price": 11.49, "total_price": 22.98}]',
 55.95, 'confirmed', 'obo', '2025-07-21 16:45:04', '2025-07-21 16:45:04'),

-- Another user's orders
('ORD-20250721100505-2', 'alice.johnson@email.com', 'pizza-agent-demo',
 '{"name": "Alice Johnson", "email": "alice.johnson@email.com", "phone": "+1-555-0789"}',
 '[{"menu_item_id": 5, "name": "Veggie Garden", "quantity": 2, "size": "small", "unit_price": 11.99, "total_price": 23.98, "special_instructions": "No olives please"}]',
 23.98, 'out_for_delivery', 'obo', '2025-07-21 10:05:05', '2025-07-21 10:25:05'),

-- Recent order for demo user
('ORD-20250721173006-1', 'demo-user-123', 'pizza-agent-demo',
 '{"name": "John Doe", "email": "john.doe@example.com", "phone": "+1-555-0123"}',
 '[{"menu_item_id": 2, "name": "Four Cheese Deluxe", "quantity": 1, "size": "medium", "unit_price": 12.99, "total_price": 12.99}, {"menu_item_id": 3, "name": "Marinara Special", "quantity": 1, "size": "small", "unit_price": 11.49, "total_price": 11.49}]',
 24.48, 'pending', 'obo', '2025-07-21 17:30:06', '2025-07-21 17:30:06')

ON CONFLICT (order_id) DO NOTHING;