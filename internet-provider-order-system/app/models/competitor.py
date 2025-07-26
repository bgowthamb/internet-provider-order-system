from app import db
from datetime import datetime
import json

class Competitor(db.Model):
    __tablename__ = 'competitors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    website = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Competitor classification
    competitor_type = db.Column(db.String(20), default='direct')  # direct, indirect, regional
    market_share = db.Column(db.Float)  # percentage
    service_area = db.Column(db.Text)  # JSON string of service areas
    
    # Competitive positioning
    price_positioning = db.Column(db.String(20))  # premium, competitive, budget
    service_quality_rating = db.Column(db.Float)  # 1-5 scale
    customer_satisfaction_score = db.Column(db.Float)  # 1-5 scale
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_price_update = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prices = db.relationship('CompetitorPrice', backref='competitor', lazy='dynamic')
    
    def get_service_areas_list(self):
        """Get service areas as a list"""
        if self.service_area:
            try:
                return json.loads(self.service_area)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_service_areas_list(self, areas_list):
        """Set service areas from a list"""
        self.service_area = json.dumps(areas_list)
    
    def get_competitive_position(self):
        """Get competitive position based on pricing and quality"""
        if self.price_positioning == 'premium' and self.service_quality_rating >= 4.0:
            return 'high_end'
        elif self.price_positioning == 'competitive' and self.service_quality_rating >= 3.5:
            return 'mid_market'
        else:
            return 'value'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'website': self.website,
            'competitor_type': self.competitor_type,
            'market_share': self.market_share,
            'service_areas': self.get_service_areas_list(),
            'price_positioning': self.price_positioning,
            'service_quality_rating': self.service_quality_rating,
            'customer_satisfaction_score': self.customer_satisfaction_score,
            'competitive_position': self.get_competitive_position(),
            'is_active': self.is_active,
            'last_price_update': self.last_price_update.isoformat() if self.last_price_update else None
        }
    
    def __repr__(self):
        return f'<Competitor {self.name}>'

class CompetitorPrice(db.Model):
    __tablename__ = 'competitor_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitors.id'), nullable=False)
    
    # Product matching
    speed_tier = db.Column(db.String(20), nullable=False)  # basic, standard, high_speed, gigabit
    internet_speed = db.Column(db.Integer)  # Mbps
    data_cap = db.Column(db.Integer)  # GB
    
    # Pricing information
    monthly_price = db.Column(db.Float, nullable=False)
    promotional_price = db.Column(db.Float)
    promotional_duration = db.Column(db.Integer)  # months
    installation_fee = db.Column(db.Float, default=0.0)
    activation_fee = db.Column(db.Float, default=0.0)
    contract_length = db.Column(db.Integer)  # months
    
    # Additional features and terms
    features = db.Column(db.Text)  # JSON string of features
    terms_conditions = db.Column(db.Text)
    
    # Price tracking
    price_change_date = db.Column(db.DateTime, default=datetime.utcnow)
    price_change_type = db.Column(db.String(20))  # increase, decrease, new
    previous_price = db.Column(db.Float)
    
    # Data source and reliability
    data_source = db.Column(db.String(50))  # website, phone, agent, third_party
    confidence_score = db.Column(db.Float, default=1.0)  # 0-1 scale
    last_verified = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    
    def get_effective_price(self, months=12):
        """Calculate effective price over a period including fees"""
        if self.promotional_price and self.promotional_duration:
            promo_months = min(self.promotional_duration, months)
            regular_months = months - promo_months
            total_cost = (self.promotional_price * promo_months) + (self.monthly_price * regular_months)
        else:
            total_cost = self.monthly_price * months
        
        # Add one-time fees
        total_cost += self.installation_fee + self.activation_fee
        
        return total_cost / months
    
    def get_price_comparison_score(self, our_price):
        """Get price comparison score against our price"""
        if our_price <= 0:
            return 0
        
        competitor_effective = self.get_effective_price()
        price_difference = (competitor_effective - our_price) / our_price
        
        if price_difference <= -0.1:  # Competitor is 10%+ cheaper
            return 1.0
        elif price_difference <= 0:  # Competitor is cheaper or same
            return 0.8
        elif price_difference <= 0.1:  # Competitor is up to 10% more expensive
            return 0.6
        elif price_difference <= 0.2:  # Competitor is 10-20% more expensive
            return 0.4
        else:  # Competitor is 20%+ more expensive
            return 0.2
    
    def is_price_competitive(self, our_price, threshold=0.1):
        """Check if competitor price is competitive against our price"""
        competitor_effective = self.get_effective_price()
        price_difference = (competitor_effective - our_price) / our_price
        return price_difference <= threshold
    
    def to_dict(self):
        return {
            'id': self.id,
            'competitor_name': self.competitor.name if self.competitor else 'Unknown',
            'speed_tier': self.speed_tier,
            'internet_speed': self.internet_speed,
            'data_cap': self.data_cap,
            'monthly_price': self.monthly_price,
            'promotional_price': self.promotional_price,
            'promotional_duration': self.promotional_duration,
            'installation_fee': self.installation_fee,
            'activation_fee': self.activation_fee,
            'contract_length': self.contract_length,
            'features': self.get_features_list(),
            'effective_price': self.get_effective_price(),
            'data_source': self.data_source,
            'confidence_score': self.confidence_score,
            'last_verified': self.last_verified.isoformat() if self.last_verified else None,
            'price_change_date': self.price_change_date.isoformat() if self.price_change_date else None
        }
    
    def __repr__(self):
        return f'<CompetitorPrice {self.competitor.name if self.competitor else "Unknown"}: {self.speed_tier} - ${self.monthly_price}>' 