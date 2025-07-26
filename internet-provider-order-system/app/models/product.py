from app import db
from datetime import datetime
import json

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ProductCategory {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'), nullable=False)
    
    # Product specifications
    internet_speed = db.Column(db.Integer)  # Mbps
    data_cap = db.Column(db.Integer)  # GB, None for unlimited
    contract_length = db.Column(db.Integer)  # months, 0 for no contract
    installation_fee = db.Column(db.Float, default=0.0)
    activation_fee = db.Column(db.Float, default=0.0)
    
    # Pricing information
    base_price = db.Column(db.Float, nullable=False)
    promotional_price = db.Column(db.Float)
    promotional_duration = db.Column(db.Integer)  # months
    price_after_promotion = db.Column(db.Float)
    
    # Product features (stored as JSON)
    features = db.Column(db.Text)  # JSON string of features
    add_ons = db.Column(db.Text)  # JSON string of available add-ons
    
    # Product status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    stock_quantity = db.Column(db.Integer, default=-1)  # -1 for unlimited
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    price_history = db.relationship('PriceHistory', backref='product', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)
        if not self.product_code:
            self.product_code = self.generate_product_code()
    
    def generate_product_code(self):
        """Generate unique product code"""
        import random
        import string
        prefix = 'PROD'
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{suffix}"
    
    def get_features_list(self):
        """Get features as a list"""
        if self.features:
            try:
                return json.loads(self.features)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_features_list(self, features_list):
        """Set features from a list"""
        self.features = json.dumps(features_list)
    
    def get_add_ons_list(self):
        """Get add-ons as a list"""
        if self.add_ons:
            try:
                return json.loads(self.add_ons)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_add_ons_list(self, add_ons_list):
        """Set add-ons from a list"""
        self.add_ons = json.dumps(add_ons_list)
    
    def get_current_price(self, customer_tier='tier_3'):
        """Get current price based on customer tier"""
        # Base pricing logic - can be enhanced with ML models
        if customer_tier == 'tier_1':
            return self.base_price * 0.85  # 15% discount for premium customers
        elif customer_tier == 'tier_2':
            return self.base_price * 0.90  # 10% discount for standard customers
        else:
            return self.base_price
    
    def get_promotional_price(self, customer_tier='tier_3'):
        """Get promotional price if available"""
        if self.promotional_price:
            base_promo = self.promotional_price
            if customer_tier == 'tier_1':
                return base_promo * 0.85
            elif customer_tier == 'tier_2':
                return base_promo * 0.90
            else:
                return base_promo
        return None
    
    def is_available(self):
        """Check if product is available for purchase"""
        return self.is_active and (self.stock_quantity == -1 or self.stock_quantity > 0)
    
    def get_speed_tier(self):
        """Get speed tier classification"""
        if self.internet_speed >= 1000:
            return 'gigabit'
        elif self.internet_speed >= 500:
            return 'high_speed'
        elif self.internet_speed >= 100:
            return 'standard'
        else:
            return 'basic'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_code': self.product_code,
            'name': self.name,
            'description': self.description,
            'category': self.category.name if self.category else None,
            'internet_speed': self.internet_speed,
            'data_cap': self.data_cap,
            'contract_length': self.contract_length,
            'base_price': self.base_price,
            'promotional_price': self.promotional_price,
            'features': self.get_features_list(),
            'add_ons': self.get_add_ons_list(),
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'speed_tier': self.get_speed_tier(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Product {self.product_code}: {self.name}>' 