from app import db
from datetime import datetime
import json

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Order details
    order_type = db.Column(db.String(20), default='new')  # new, upgrade, downgrade, addon
    order_status = db.Column(db.String(20), default='pending')  # pending, confirmed, processing, completed, cancelled
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Pricing information
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    
    # Promotional and discount information
    promotional_code = db.Column(db.String(20))
    discount_reason = db.Column(db.String(100))
    negotiated_price = db.Column(db.Float)
    price_match_competitor = db.Column(db.String(100))
    
    # Installation and scheduling
    installation_date = db.Column(db.DateTime)
    installation_time_slot = db.Column(db.String(20))
    installation_address = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    def generate_order_number(self):
        """Generate unique order number"""
        import random
        import string
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"ORD{timestamp}{suffix}"
    
    def calculate_totals(self):
        """Calculate order totals"""
        self.subtotal = sum(item.total_price for item in self.items)
        self.tax_amount = self.subtotal * 0.08  # 8% tax rate
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
    
    def apply_discount(self, amount, reason):
        """Apply discount to order"""
        self.discount_amount = amount
        self.discount_reason = reason
        self.calculate_totals()
    
    def apply_promotional_code(self, code):
        """Apply promotional code"""
        # This would typically validate against a promotional codes table
        self.promotional_code = code
        # Apply 10% discount for promotional codes
        self.discount_amount = self.subtotal * 0.10
        self.calculate_totals()
    
    def set_negotiated_price(self, price, competitor=None):
        """Set negotiated price based on competitor matching"""
        self.negotiated_price = price
        if competitor:
            self.price_match_competitor = competitor
        self.calculate_totals()
    
    def get_order_summary(self):
        """Get order summary for display"""
        return {
            'order_number': self.order_number,
            'customer_name': self.customer.get_full_name() if self.customer else 'Unknown',
            'status': self.order_status,
            'total_amount': self.total_amount,
            'item_count': self.items.count(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'order_type': self.order_type,
            'order_status': self.order_status,
            'priority': self.priority,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'discount_amount': self.discount_amount,
            'total_amount': self.total_amount,
            'promotional_code': self.promotional_code,
            'discount_reason': self.discount_reason,
            'negotiated_price': self.negotiated_price,
            'price_match_competitor': self.price_match_competitor,
            'installation_date': self.installation_date.isoformat() if self.installation_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }
    
    def __repr__(self):
        return f'<Order {self.order_number}: {self.order_status}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Item details
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Pricing adjustments
    discount_percentage = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    
    # Product configuration (for add-ons and customizations)
    configuration = db.Column(db.Text)  # JSON string for product configuration
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(OrderItem, self).__init__(**kwargs)
        self.calculate_total()
    
    def calculate_total(self):
        """Calculate item total price"""
        base_total = self.unit_price * self.quantity
        discount = (base_total * self.discount_percentage / 100) + self.discount_amount
        self.total_price = base_total - discount
    
    def apply_discount(self, percentage=None, amount=None):
        """Apply discount to item"""
        if percentage is not None:
            self.discount_percentage = percentage
        if amount is not None:
            self.discount_amount = amount
        self.calculate_total()
    
    def get_configuration_dict(self):
        """Get configuration as dictionary"""
        if self.configuration:
            try:
                return json.loads(self.configuration)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_configuration_dict(self, config_dict):
        """Set configuration from dictionary"""
        self.configuration = json.dumps(config_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown',
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'discount_percentage': self.discount_percentage,
            'discount_amount': self.discount_amount,
            'configuration': self.get_configuration_dict()
        }
    
    def __repr__(self):
        return f'<OrderItem {self.id}: {self.product.name if self.product else "Unknown"} x {self.quantity}>' 