from app import db
from datetime import datetime
import json

class PricingModel(db.Model):
    __tablename__ = 'pricing_models'
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), unique=True, nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # regression, classification, ensemble
    
    # Model parameters and configuration
    model_config = db.Column(db.Text)  # JSON string of model parameters
    feature_columns = db.Column(db.Text)  # JSON string of feature columns
    target_column = db.Column(db.String(50))
    
    # Model performance metrics
    accuracy_score = db.Column(db.Float)
    precision_score = db.Column(db.Float)
    recall_score = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    mse_score = db.Column(db.Float)
    mae_score = db.Column(db.Float)
    
    # Model file paths
    model_file_path = db.Column(db.String(200))
    scaler_file_path = db.Column(db.String(200))
    encoder_file_path = db.Column(db.String(200))
    
    # Model status
    is_active = db.Column(db.Boolean, default=False)
    is_production = db.Column(db.Boolean, default=False)
    version = db.Column(db.String(20), default='1.0.0')
    
    # Training information
    training_data_size = db.Column(db.Integer)
    training_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_model_config_dict(self):
        """Get model configuration as dictionary"""
        if self.model_config:
            try:
                return json.loads(self.model_config)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_model_config_dict(self, config_dict):
        """Set model configuration from dictionary"""
        self.model_config = json.dumps(config_dict)
    
    def get_feature_columns_list(self):
        """Get feature columns as a list"""
        if self.feature_columns:
            try:
                return json.loads(self.feature_columns)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_feature_columns_list(self, columns_list):
        """Set feature columns from a list"""
        self.feature_columns = json.dumps(columns_list)
    
    def get_performance_summary(self):
        """Get model performance summary"""
        if self.model_type == 'classification':
            return {
                'accuracy': self.accuracy_score,
                'precision': self.precision_score,
                'recall': self.recall_score,
                'f1_score': self.f1_score
            }
        else:  # regression
            return {
                'mse': self.mse_score,
                'mae': self.mae_score
            }
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_name': self.model_name,
            'model_type': self.model_type,
            'version': self.version,
            'is_active': self.is_active,
            'is_production': self.is_production,
            'performance': self.get_performance_summary(),
            'training_data_size': self.training_data_size,
            'training_date': self.training_date.isoformat() if self.training_date else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    def __repr__(self):
        return f'<PricingModel {self.model_name} v{self.version}>'

class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Price information
    base_price = db.Column(db.Float, nullable=False)
    promotional_price = db.Column(db.Float)
    effective_price = db.Column(db.Float, nullable=False)
    
    # Price change tracking
    price_change_type = db.Column(db.String(20))  # increase, decrease, new, promotional
    price_change_reason = db.Column(db.String(100))
    previous_price = db.Column(db.Float)
    price_change_percentage = db.Column(db.Float)
    
    # Market context
    competitor_avg_price = db.Column(db.Float)
    market_demand_score = db.Column(db.Float)  # 0-1 scale
    seasonality_factor = db.Column(db.Float, default=1.0)
    
    # ML model predictions
    predicted_price = db.Column(db.Float)
    confidence_score = db.Column(db.Float)  # 0-1 scale
    model_used = db.Column(db.String(100))
    
    # Timestamps
    effective_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_price_change_percentage(self):
        """Calculate price change percentage"""
        if self.previous_price and self.previous_price > 0:
            self.price_change_percentage = ((self.effective_price - self.previous_price) / self.previous_price) * 100
        else:
            self.price_change_percentage = 0.0
    
    def get_price_trend(self):
        """Get price trend direction"""
        if self.price_change_percentage > 5:
            return 'increasing'
        elif self.price_change_percentage < -5:
            return 'decreasing'
        else:
            return 'stable'
    
    def is_promotional_price(self):
        """Check if this is a promotional price"""
        return self.promotional_price is not None and self.promotional_price < self.base_price
    
    def get_competitive_position(self):
        """Get competitive position based on competitor average"""
        if not self.competitor_avg_price:
            return 'unknown'
        
        price_difference = (self.effective_price - self.competitor_avg_price) / self.competitor_avg_price
        
        if price_difference <= -0.1:
            return 'competitive'
        elif price_difference <= 0.05:
            return 'market_rate'
        else:
            return 'premium'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown',
            'base_price': self.base_price,
            'promotional_price': self.promotional_price,
            'effective_price': self.effective_price,
            'price_change_type': self.price_change_type,
            'price_change_reason': self.price_change_reason,
            'price_change_percentage': self.price_change_percentage,
            'competitor_avg_price': self.competitor_avg_price,
            'market_demand_score': self.market_demand_score,
            'predicted_price': self.predicted_price,
            'confidence_score': self.confidence_score,
            'model_used': self.model_used,
            'price_trend': self.get_price_trend(),
            'competitive_position': self.get_competitive_position(),
            'effective_date': self.effective_date.isoformat() if self.effective_date else None
        }
    
    def __repr__(self):
        return f'<PriceHistory {self.product.name if self.product else "Unknown"}: ${self.effective_price}>' 