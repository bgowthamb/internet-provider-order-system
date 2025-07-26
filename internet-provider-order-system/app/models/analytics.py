from app import db
from datetime import datetime
import json

class CustomerAnalytics(db.Model):
    __tablename__ = 'customer_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Purchase behavior
    total_orders = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    avg_order_value = db.Column(db.Float, default=0.0)
    first_order_date = db.Column(db.DateTime)
    last_order_date = db.Column(db.DateTime)
    
    # Product preferences
    preferred_speed_tier = db.Column(db.String(20))
    preferred_product_category = db.Column(db.String(50))
    most_purchased_product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    # Customer lifecycle
    customer_lifetime_days = db.Column(db.Integer, default=0)
    days_since_last_order = db.Column(db.Integer, default=0)
    order_frequency_days = db.Column(db.Float, default=0.0)
    
    # Behavioral scores
    loyalty_score = db.Column(db.Float, default=0.0)  # 0-1 scale
    price_sensitivity_score = db.Column(db.Float, default=0.5)  # 0-1 scale
    upgrade_probability = db.Column(db.Float, default=0.0)  # 0-1 scale
    churn_risk_score = db.Column(db.Float, default=0.0)  # 0-1 scale
    
    # Response to promotions
    promotional_response_rate = db.Column(db.Float, default=0.0)  # 0-1 scale
    discount_usage_frequency = db.Column(db.Float, default=0.0)
    price_match_requests = db.Column(db.Integer, default=0)
    
    # Communication preferences
    preferred_contact_method = db.Column(db.String(20))
    response_rate_to_offers = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_loyalty_score(self):
        """Calculate customer loyalty score based on various factors"""
        score = 0.0
        
        # Order frequency (higher is better)
        if self.order_frequency_days > 0:
            if self.order_frequency_days <= 30:
                score += 0.3
            elif self.order_frequency_days <= 90:
                score += 0.2
            elif self.order_frequency_days <= 180:
                score += 0.1
        
        # Total spent (higher is better)
        if self.total_spent > 5000:
            score += 0.3
        elif self.total_spent > 2000:
            score += 0.2
        elif self.total_spent > 500:
            score += 0.1
        
        # Customer lifetime (longer is better)
        if self.customer_lifetime_days > 365:
            score += 0.2
        elif self.customer_lifetime_days > 180:
            score += 0.1
        
        # Recent activity (more recent is better)
        if self.days_since_last_order <= 30:
            score += 0.2
        elif self.days_since_last_order <= 90:
            score += 0.1
        
        self.loyalty_score = min(score, 1.0)
        return self.loyalty_score
    
    def calculate_price_sensitivity(self):
        """Calculate price sensitivity based on discount usage and price matching"""
        sensitivity = 0.5  # Default neutral
        
        # Discount usage (higher usage = higher sensitivity)
        if self.discount_usage_frequency > 0.8:
            sensitivity += 0.3
        elif self.discount_usage_frequency > 0.5:
            sensitivity += 0.2
        elif self.discount_usage_frequency > 0.2:
            sensitivity += 0.1
        
        # Price match requests (more requests = higher sensitivity)
        if self.price_match_requests > 3:
            sensitivity += 0.2
        elif self.price_match_requests > 1:
            sensitivity += 0.1
        
        # Promotional response (higher response = higher sensitivity)
        if self.promotional_response_rate > 0.8:
            sensitivity += 0.2
        elif self.promotional_response_rate > 0.5:
            sensitivity += 0.1
        
        self.price_sensitivity_score = min(sensitivity, 1.0)
        return self.price_sensitivity_score
    
    def get_customer_segment(self):
        """Get customer segment based on analytics"""
        if self.loyalty_score >= 0.8 and self.total_spent > 3000:
            return 'vip'
        elif self.loyalty_score >= 0.6 and self.total_spent > 1000:
            return 'loyal'
        elif self.churn_risk_score >= 0.7:
            return 'at_risk'
        elif self.days_since_last_order > 365:
            return 'inactive'
        else:
            return 'regular'
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'total_orders': self.total_orders,
            'total_spent': self.total_spent,
            'avg_order_value': self.avg_order_value,
            'customer_lifetime_days': self.customer_lifetime_days,
            'days_since_last_order': self.days_since_last_order,
            'loyalty_score': self.loyalty_score,
            'price_sensitivity_score': self.price_sensitivity_score,
            'upgrade_probability': self.upgrade_probability,
            'churn_risk_score': self.churn_risk_score,
            'customer_segment': self.get_customer_segment(),
            'preferred_speed_tier': self.preferred_speed_tier,
            'promotional_response_rate': self.promotional_response_rate,
            'price_match_requests': self.price_match_requests,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<CustomerAnalytics {self.customer_id}: {self.get_customer_segment()}>'

class OrderAnalytics(db.Model):
    __tablename__ = 'order_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    
    # Order performance metrics
    conversion_score = db.Column(db.Float, default=0.0)  # 0-1 scale
    profitability_score = db.Column(db.Float, default=0.0)  # 0-1 scale
    customer_satisfaction_prediction = db.Column(db.Float, default=0.0)  # 0-1 scale
    
    # Pricing analysis
    price_competitiveness_score = db.Column(db.Float, default=0.0)  # 0-1 scale
    discount_effectiveness = db.Column(db.Float, default=0.0)  # 0-1 scale
    price_elasticity = db.Column(db.Float, default=0.0)
    
    # Market context
    market_demand_level = db.Column(db.Float, default=0.5)  # 0-1 scale
    competitor_pressure_score = db.Column(db.Float, default=0.0)  # 0-1 scale
    seasonality_impact = db.Column(db.Float, default=1.0)
    
    # ML predictions
    predicted_order_value = db.Column(db.Float)
    predicted_customer_lifetime_value = db.Column(db.Float)
    churn_risk_after_order = db.Column(db.Float, default=0.0)
    
    # Feature importance for ML
    key_factors = db.Column(db.Text)  # JSON string of important factors
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_key_factors_dict(self):
        """Get key factors as dictionary"""
        if self.key_factors:
            try:
                return json.loads(self.key_factors)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_key_factors_dict(self, factors_dict):
        """Set key factors from dictionary"""
        self.key_factors = json.dumps(factors_dict)
    
    def calculate_conversion_score(self):
        """Calculate conversion likelihood score"""
        score = 0.5  # Base score
        
        # Price competitiveness
        if self.price_competitiveness_score > 0.8:
            score += 0.2
        elif self.price_competitiveness_score > 0.6:
            score += 0.1
        
        # Market demand
        if self.market_demand_level > 0.7:
            score += 0.15
        elif self.market_demand_level > 0.5:
            score += 0.1
        
        # Customer satisfaction prediction
        if self.customer_satisfaction_prediction > 0.8:
            score += 0.15
        elif self.customer_satisfaction_prediction > 0.6:
            score += 0.1
        
        self.conversion_score = min(score, 1.0)
        return self.conversion_score
    
    def calculate_profitability_score(self):
        """Calculate profitability score"""
        score = 0.5  # Base score
        
        # Higher profitability for better margins
        if self.profitability_score > 0.8:
            score += 0.3
        elif self.profitability_score > 0.6:
            score += 0.2
        elif self.profitability_score > 0.4:
            score += 0.1
        
        # Lower churn risk increases profitability
        if self.churn_risk_after_order < 0.2:
            score += 0.2
        elif self.churn_risk_after_order < 0.4:
            score += 0.1
        
        self.profitability_score = min(score, 1.0)
        return self.profitability_score
    
    def get_order_priority(self):
        """Get order priority based on analytics"""
        if self.conversion_score > 0.8 and self.profitability_score > 0.7:
            return 'high'
        elif self.conversion_score > 0.6 or self.profitability_score > 0.6:
            return 'medium'
        else:
            return 'low'
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'conversion_score': self.conversion_score,
            'profitability_score': self.profitability_score,
            'customer_satisfaction_prediction': self.customer_satisfaction_prediction,
            'price_competitiveness_score': self.price_competitiveness_score,
            'discount_effectiveness': self.discount_effectiveness,
            'market_demand_level': self.market_demand_level,
            'competitor_pressure_score': self.competitor_pressure_score,
            'predicted_order_value': self.predicted_order_value,
            'predicted_customer_lifetime_value': self.predicted_customer_lifetime_value,
            'churn_risk_after_order': self.churn_risk_after_order,
            'order_priority': self.get_order_priority(),
            'key_factors': self.get_key_factors_dict(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<OrderAnalytics {self.order_id}: {self.get_order_priority()}>' 