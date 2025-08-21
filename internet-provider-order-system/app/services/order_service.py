from app import db
from app.models import Order, OrderItem, Product, Customer
from app.services.pricing_service import PricingService
from datetime import datetime
import uuid
import json

class OrderService:
    def __init__(self):
        self.pricing_service = PricingService()
    
    def get_order_by_id(self, order_id):
        """Get order by ID"""
        return Order.query.get(order_id)
    
    def get_all_orders(self):
        """Get all orders"""
        return Order.query.order_by(Order.created_at.desc()).all()
    
    def create_order(self, data):
        """Create a new order with optimal pricing"""
        # Generate order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create order
        order = Order(
            order_number=order_number,
            customer_id=data['customer_id'],
            created_by_id=data['created_by'],
            order_status='pending',
            total_amount=0,
            promotional_code=data.get('promotional_code'),
            negotiated_price=data.get('negotiated_price', 0)
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Add order items with optimal pricing
        total_amount = 0
        for item_data in data['items']:
            product = Product.query.get(item_data['product_id'])
            if product:
                # Get optimal price for this customer and product
                pricing_info = self.pricing_service.get_optimal_price_for_customer(
                    product.id, 
                    data['customer_id']
                )
                
                unit_price = pricing_info['optimal_price']
                quantity = item_data.get('quantity', 1)
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price,
                    configuration=json.dumps(item_data.get('configuration', {}))
                )
                
                db.session.add(order_item)
                total_amount += unit_price * quantity
        
        # Update order total
        order.total_amount = total_amount
        
        # Apply negotiated price if provided
        if data.get('negotiated_price'):
            order.negotiated_price = data['negotiated_price']
            order.total_amount = data['negotiated_price']
        
        db.session.commit()
        return order
    
    def update_order_status(self, order_id, status):
        """Update order status"""
        order = self.get_order_by_id(order_id)
        if order:
            order.order_status = status
            order.updated_at = datetime.now()
            db.session.commit()
        return order
    
    def get_order_items(self, order_id):
        """Get order items"""
        return OrderItem.query.filter_by(order_id=order_id).all()
    
    def calculate_order_total(self, order_id):
        """Calculate order total"""
        order_items = self.get_order_items(order_id)
        return sum(item.unit_price * item.quantity for item in order_items)
    
    def apply_promotional_code(self, order_id, code):
        """Apply promotional code to order"""
        order = self.get_order_by_id(order_id)
        if order:
            # Simple promotional code logic (10% discount)
            if code.upper() == 'SAVE10':
                discount = order.total_amount * 0.1
                order.total_amount -= discount
                order.promotional_code = code
                db.session.commit()
                return {'success': True, 'discount': discount}
            else:
                return {'success': False, 'message': 'Invalid promotional code'}
        return {'success': False, 'message': 'Order not found'}
    
    def get_orders_by_customer(self, customer_id):
        """Get all orders for a customer"""
        return Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    
    def get_orders_by_status(self, status):
        """Get orders by status"""
        return Order.query.filter_by(order_status=status).order_by(Order.created_at.desc()).all()
    
    def get_recent_orders(self, limit=10):
        """Get recent orders"""
        return Order.query.order_by(Order.created_at.desc()).limit(limit).all()
