import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, classification_report
import joblib
import os
from datetime import datetime, timedelta
import json

from app import db
from app.models import Customer, Product, Order, OrderItem, CompetitorPrice, CustomerAnalytics, OrderAnalytics, PricingModel

class MLService:
    def __init__(self):
        self.models_dir = 'ml_models'
        self.ensure_models_directory()
    
    def ensure_models_directory(self):
        """Ensure models directory exists"""
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def prepare_customer_data(self):
        """Prepare customer data for ML training"""
        # Get customer data with analytics
        customers = Customer.query.all()
        customer_data = []
        
        for customer in customers:
            analytics = CustomerAnalytics.query.filter_by(customer_id=customer.id).first()
            
            if analytics:
                data = {
                    'customer_id': customer.id,
                    'total_spent': customer.total_spent,
                    'avg_monthly_bill': customer.avg_monthly_bill,
                    'credit_score': customer.credit_score or 0,
                    'household_size': customer.household_size or 1,
                    'total_orders': analytics.total_orders,
                    'avg_order_value': analytics.avg_order_value,
                    'customer_lifetime_days': analytics.customer_lifetime_days,
                    'days_since_last_order': analytics.days_since_last_order,
                    'loyalty_score': analytics.loyalty_score,
                    'price_sensitivity_score': analytics.price_sensitivity_score,
                    'upgrade_probability': analytics.upgrade_probability,
                    'churn_risk_score': analytics.churn_risk_score,
                    'promotional_response_rate': analytics.promotional_response_rate,
                    'price_match_requests': analytics.price_match_requests
                }
                customer_data.append(data)
        
        return pd.DataFrame(customer_data)
    
    def prepare_pricing_data(self):
        """Prepare pricing data for ML training"""
        # Get product pricing history
        price_history = db.session.query(PriceHistory).all()
        pricing_data = []
        
        for price in price_history:
            data = {
                'product_id': price.product_id,
                'base_price': price.base_price,
                'effective_price': price.effective_price,
                'competitor_avg_price': price.competitor_avg_price or 0,
                'market_demand_score': price.market_demand_score or 0.5,
                'seasonality_factor': price.seasonality_factor,
                'price_change_percentage': price.price_change_percentage or 0,
                'predicted_price': price.predicted_price or 0
            }
            pricing_data.append(data)
        
        return pd.DataFrame(pricing_data)
    
    def prepare_order_data(self):
        """Prepare order data for ML training"""
        # Get order data with analytics
        orders = Order.query.all()
        order_data = []
        
        for order in orders:
            analytics = OrderAnalytics.query.filter_by(order_id=order.id).first()
            
            if analytics:
                data = {
                    'order_id': order.id,
                    'customer_id': order.customer_id,
                    'subtotal': order.subtotal,
                    'total_amount': order.total_amount,
                    'discount_amount': order.discount_amount,
                    'conversion_score': analytics.conversion_score,
                    'profitability_score': analytics.profitability_score,
                    'price_competitiveness_score': analytics.price_competitiveness_score,
                    'market_demand_level': analytics.market_demand_level,
                    'competitor_pressure_score': analytics.competitor_pressure_score,
                    'predicted_order_value': analytics.predicted_order_value or 0
                }
                order_data.append(data)
        
        return pd.DataFrame(order_data)
    
    def train_price_prediction_model(self, model_name='price_prediction_v1'):
        """Train price prediction model"""
        # Prepare data
        pricing_df = self.prepare_pricing_data()
        
        if pricing_df.empty:
            return {'error': 'No pricing data available for training'}
        
        # Feature engineering
        pricing_df['price_ratio'] = pricing_df['effective_price'] / pricing_df['base_price']
        pricing_df['competitor_ratio'] = pricing_df['effective_price'] / pricing_df['competitor_avg_price'].replace(0, 1)
        pricing_df['demand_adjusted_price'] = pricing_df['effective_price'] * pricing_df['market_demand_score']
        
        # Select features
        feature_columns = [
            'base_price', 'competitor_avg_price', 'market_demand_score', 
            'seasonality_factor', 'price_ratio', 'competitor_ratio', 'demand_adjusted_price'
        ]
        
        X = pricing_df[feature_columns].fillna(0)
        y = pricing_df['effective_price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Save model
        model_path = os.path.join(self.models_dir, f'{model_name}.joblib')
        joblib.dump(model, model_path)
        
        # Save scaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_train)
        scaler_path = os.path.join(self.models_dir, f'{model_name}_scaler.joblib')
        joblib.dump(scaler, scaler_path)
        
        # Save model metadata to database
        model_record = PricingModel(
            model_name=model_name,
            model_type='regression',
            model_config=json.dumps({'n_estimators': 100, 'random_state': 42}),
            feature_columns=json.dumps(feature_columns),
            target_column='effective_price',
            mse_score=mse,
            mae_score=mae,
            model_file_path=model_path,
            scaler_file_path=scaler_path,
            training_data_size=len(pricing_df),
            training_date=datetime.utcnow(),
            is_active=True
        )
        
        db.session.add(model_record)
        db.session.commit()
        
        return {
            'model_name': model_name,
            'mse': mse,
            'mae': mae,
            'training_samples': len(pricing_df),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
    
    def train_customer_churn_model(self, model_name='churn_prediction_v1'):
        """Train customer churn prediction model"""
        # Prepare data
        customer_df = self.prepare_customer_data()
        
        if customer_df.empty:
            return {'error': 'No customer data available for training'}
        
        # Create churn target (customers with high churn risk)
        customer_df['is_churn_risk'] = (customer_df['churn_risk_score'] > 0.7).astype(int)
        
        # Feature engineering
        customer_df['spending_per_order'] = customer_df['total_spent'] / customer_df['total_orders'].replace(0, 1)
        customer_df['order_frequency'] = customer_df['customer_lifetime_days'] / customer_df['total_orders'].replace(0, 1)
        
        # Select features
        feature_columns = [
            'total_spent', 'avg_monthly_bill', 'credit_score', 'household_size',
            'total_orders', 'avg_order_value', 'customer_lifetime_days', 
            'days_since_last_order', 'loyalty_score', 'price_sensitivity_score',
            'promotional_response_rate', 'price_match_requests', 'spending_per_order',
            'order_frequency'
        ]
        
        X = customer_df[feature_columns].fillna(0)
        y = customer_df['is_churn_risk']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Save model
        model_path = os.path.join(self.models_dir, f'{model_name}.joblib')
        joblib.dump(model, model_path)
        
        # Save model metadata to database
        model_record = PricingModel(
            model_name=model_name,
            model_type='classification',
            model_config=json.dumps({'n_estimators': 100, 'random_state': 42}),
            feature_columns=json.dumps(feature_columns),
            target_column='is_churn_risk',
            accuracy_score=accuracy,
            model_file_path=model_path,
            training_data_size=len(customer_df),
            training_date=datetime.utcnow(),
            is_active=True
        )
        
        db.session.add(model_record)
        db.session.commit()
        
        return {
            'model_name': model_name,
            'accuracy': accuracy,
            'training_samples': len(customer_df),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
    
    def predict_optimal_price(self, product_id, customer_id=None, competitor_prices=None):
        """Predict optimal price for a product"""
        # Get active price prediction model
        model_record = PricingModel.query.filter_by(
            model_type='regression', 
            is_active=True
        ).order_by(PricingModel.training_date.desc()).first()
        
        if not model_record:
            return {'error': 'No active price prediction model found'}
        
        # Load model
        model = joblib.load(model_record.model_file_path)
        scaler = joblib.load(model_record.scaler_file_path)
        
        # Get product data
        product = Product.query.get(product_id)
        if not product:
            return {'error': 'Product not found'}
        
        # Get customer data if provided
        customer_data = {}
        if customer_id:
            customer = Customer.query.get(customer_id)
            if customer:
                analytics = CustomerAnalytics.query.filter_by(customer_id=customer_id).first()
                if analytics:
                    customer_data = {
                        'price_sensitivity': analytics.price_sensitivity_score,
                        'loyalty_score': analytics.loyalty_score,
                        'customer_segment': customer.get_customer_segment()
                    }
        
        # Get competitor prices
        if not competitor_prices:
            competitor_prices = CompetitorPrice.query.filter_by(
                speed_tier=product.get_speed_tier()
            ).all()
        
        avg_competitor_price = np.mean([cp.get_effective_price() for cp in competitor_prices]) if competitor_prices else product.base_price
        
        # Prepare features
        features = {
            'base_price': product.base_price,
            'competitor_avg_price': avg_competitor_price,
            'market_demand_score': 0.7,  # Default value
            'seasonality_factor': 1.0,   # Default value
            'price_ratio': 1.0,          # Default value
            'competitor_ratio': product.base_price / avg_competitor_price if avg_competitor_price > 0 else 1.0,
            'demand_adjusted_price': product.base_price * 0.7  # Default value
        }
        
        # Apply customer-specific adjustments
        if customer_data:
            if customer_data.get('customer_segment') == 'premium':
                features['market_demand_score'] = 0.9
            elif customer_data.get('price_sensitivity', 0.5) > 0.7:
                features['price_ratio'] = 0.9  # Lower price for price-sensitive customers
        
        # Make prediction
        X = pd.DataFrame([features])
        X_scaled = scaler.transform(X)
        predicted_price = model.predict(X_scaled)[0]
        
        # Apply business rules
        min_price = product.base_price * 0.8  # Minimum 20% discount
        max_price = product.base_price * 1.2  # Maximum 20% increase
        
        optimal_price = max(min_price, min(predicted_price, max_price))
        
        return {
            'product_id': product_id,
            'base_price': product.base_price,
            'predicted_price': predicted_price,
            'optimal_price': optimal_price,
            'confidence_score': 0.85,  # Placeholder
            'factors': {
                'competitor_pricing': avg_competitor_price,
                'customer_segment': customer_data.get('customer_segment', 'unknown'),
                'price_sensitivity': customer_data.get('price_sensitivity', 0.5)
            }
        }
    
    def predict_customer_churn_risk(self, customer_id):
        """Predict customer churn risk"""
        # Get active churn prediction model
        model_record = PricingModel.query.filter_by(
            model_type='classification', 
            is_active=True
        ).order_by(PricingModel.training_date.desc()).first()
        
        if not model_record:
            return {'error': 'No active churn prediction model found'}
        
        # Load model
        model = joblib.load(model_record.model_file_path)
        
        # Get customer data
        customer = Customer.query.get(customer_id)
        if not customer:
            return {'error': 'Customer not found'}
        
        analytics = CustomerAnalytics.query.filter_by(customer_id=customer_id).first()
        if not analytics:
            return {'error': 'Customer analytics not found'}
        
        # Prepare features
        features = {
            'total_spent': customer.total_spent,
            'avg_monthly_bill': customer.avg_monthly_bill,
            'credit_score': customer.credit_score or 0,
            'household_size': customer.household_size or 1,
            'total_orders': analytics.total_orders,
            'avg_order_value': analytics.avg_order_value,
            'customer_lifetime_days': analytics.customer_lifetime_days,
            'days_since_last_order': analytics.days_since_last_order,
            'loyalty_score': analytics.loyalty_score,
            'price_sensitivity_score': analytics.price_sensitivity_score,
            'promotional_response_rate': analytics.promotional_response_rate,
            'price_match_requests': analytics.price_match_requests,
            'spending_per_order': customer.total_spent / analytics.total_orders if analytics.total_orders > 0 else 0,
            'order_frequency': analytics.customer_lifetime_days / analytics.total_orders if analytics.total_orders > 0 else 0
        }
        
        # Make prediction
        X = pd.DataFrame([features])
        churn_probability = model.predict_proba(X)[0][1]  # Probability of churn
        
        return {
            'customer_id': customer_id,
            'churn_risk_score': churn_probability,
            'risk_level': 'high' if churn_probability > 0.7 else 'medium' if churn_probability > 0.4 else 'low',
            'recommendations': self.get_churn_prevention_recommendations(churn_probability, features)
        }
    
    def get_churn_prevention_recommendations(self, churn_probability, features):
        """Get recommendations to prevent customer churn"""
        recommendations = []
        
        if churn_probability > 0.7:
            recommendations.append("High churn risk - Consider retention offers")
            recommendations.append("Offer loyalty discounts or upgrade incentives")
            recommendations.append("Schedule proactive customer outreach")
        
        if features.get('days_since_last_order', 0) > 90:
            recommendations.append("Customer inactive - Send re-engagement offers")
        
        if features.get('price_sensitivity_score', 0.5) > 0.7:
            recommendations.append("Price-sensitive customer - Consider competitive pricing")
        
        if features.get('loyalty_score', 0) < 0.3:
            recommendations.append("Low loyalty - Focus on relationship building")
        
        return recommendations
    
    def get_model_performance_summary(self):
        """Get summary of all ML models performance"""
        models = PricingModel.query.filter_by(is_active=True).all()
        
        summary = []
        for model in models:
            summary.append({
                'model_name': model.model_name,
                'model_type': model.model_type,
                'version': model.version,
                'training_date': model.training_date.isoformat() if model.training_date else None,
                'training_samples': model.training_data_size,
                'performance': model.get_performance_summary()
            })
        
        return summary 