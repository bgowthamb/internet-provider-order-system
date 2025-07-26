from app import db
from datetime import datetime
import json

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    zip_code = db.Column(db.String(10))
    country = db.Column(db.String(64), default='USA')
    
    # Customer classification and segmentation
    customer_type = db.Column(db.String(20), default='residential')  # residential, business, enterprise
    credit_score = db.Column(db.Integer)
    income_level = db.Column(db.String(20))  # low, medium, high
    household_size = db.Column(db.Integer)
    
    # Historical data for predictive analysis
    total_spent = db.Column(db.Float, default=0.0)
    avg_monthly_bill = db.Column(db.Float, default=0.0)
    churn_risk_score = db.Column(db.Float, default=0.0)
    lifetime_value = db.Column(db.Float, default=0.0)
    
    # Behavioral data
    preferred_contact_method = db.Column(db.String(20), default='email')
    marketing_consent = db.Column(db.Boolean, default=True)
    loyalty_program_member = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_purchase_date = db.Column(db.DateTime)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    analytics = db.relationship('CustomerAnalytics', backref='customer', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Customer, self).__init__(**kwargs)
        if not self.customer_id:
            self.customer_id = self.generate_customer_id()
    
    def generate_customer_id(self):
        """Generate unique customer ID"""
        import random
        import string
        prefix = 'CUST'
        suffix = ''.join(random.choices(string.digits, k=8))
        return f"{prefix}{suffix}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_customer_segment(self):
        """Determine customer segment based on spending and behavior"""
        if self.total_spent > 5000 and self.lifetime_value > 10000:
            return 'premium'
        elif self.total_spent > 2000 and self.lifetime_value > 5000:
            return 'standard'
        else:
            return 'basic'
    
    def calculate_churn_risk(self):
        """Calculate churn risk based on various factors"""
        risk_factors = 0
        
        # Factors that increase churn risk
        if self.avg_monthly_bill > 100:
            risk_factors += 1
        if self.credit_score and self.credit_score < 600:
            risk_factors += 2
        if self.last_purchase_date:
            days_since_purchase = (datetime.utcnow() - self.last_purchase_date).days
            if days_since_purchase > 365:
                risk_factors += 3
        
        # Normalize to 0-1 scale
        self.churn_risk_score = min(risk_factors / 6, 1.0)
        return self.churn_risk_score
    
    def get_pricing_tier(self):
        """Get pricing tier for this customer"""
        segment = self.get_customer_segment()
        if segment == 'premium':
            return 'tier_1'
        elif segment == 'standard':
            return 'tier_2'
        else:
            return 'tier_3'
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'name': self.get_full_name(),
            'email': self.email,
            'phone': self.phone,
            'customer_type': self.customer_type,
            'segment': self.get_customer_segment(),
            'pricing_tier': self.get_pricing_tier(),
            'total_spent': self.total_spent,
            'avg_monthly_bill': self.avg_monthly_bill,
            'churn_risk': self.churn_risk_score,
            'lifetime_value': self.lifetime_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Customer {self.customer_id}: {self.get_full_name()}>' 