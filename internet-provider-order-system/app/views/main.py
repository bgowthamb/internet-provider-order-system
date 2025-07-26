from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Customer, Product, Order, OrderAnalytics, CustomerAnalytics
from app.services.pricing_service import PricingService
from app.services.ml_service import MLService
from datetime import datetime, timedelta
import json

main_bp = Blueprint('main', __name__)
pricing_service = PricingService()
ml_service = MLService()

@main_bp.route('/')
@login_required
def dashboard():
    """Main dashboard"""
    # Get summary statistics
    total_customers = Customer.query.count()
    total_products = Product.query.filter_by(is_active=True).count()
    total_orders = Order.query.count()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Customer analytics summary
    high_value_customers = Customer.query.filter(Customer.total_spent > 5000).count()
    at_risk_customers = CustomerAnalytics.query.filter(CustomerAnalytics.churn_risk_score > 0.7).count()
    
    # Revenue metrics
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    monthly_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
        Order.created_at >= datetime.utcnow() - timedelta(days=30)
    ).scalar() or 0
    
    return render_template('dashboard.html',
                         total_customers=total_customers,
                         total_products=total_products,
                         total_orders=total_orders,
                         recent_orders=recent_orders,
                         high_value_customers=high_value_customers,
                         at_risk_customers=at_risk_customers,
                         total_revenue=total_revenue,
                         monthly_revenue=monthly_revenue)

@main_bp.route('/pricing-optimization')
@login_required
def pricing_optimization():
    """Pricing optimization dashboard"""
    products = Product.query.filter_by(is_active=True).all()
    customers = Customer.query.limit(10).all()  # Sample customers for demo
    
    return render_template('pricing_optimization.html',
                         products=products,
                         customers=customers)

@main_bp.route('/api/optimal-price', methods=['POST'])
@login_required
def get_optimal_price():
    """API endpoint for getting optimal price"""
    data = request.get_json()
    
    product_id = data.get('product_id')
    customer_id = data.get('customer_id')
    competitor_name = data.get('competitor_name')
    
    if not product_id or not customer_id:
        return jsonify({'error': 'Product ID and Customer ID are required'}), 400
    
    result = pricing_service.get_optimal_price_for_customer(
        product_id, customer_id, competitor_name
    )
    
    return jsonify(result)

@main_bp.route('/api/price-match', methods=['POST'])
@login_required
def price_match():
    """API endpoint for price matching"""
    data = request.get_json()
    
    product_id = data.get('product_id')
    customer_id = data.get('customer_id')
    competitor_name = data.get('competitor_name')
    competitor_price = data.get('competitor_price')
    
    if not all([product_id, customer_id, competitor_name, competitor_price]):
        return jsonify({'error': 'All fields are required'}), 400
    
    result = pricing_service.price_match_competitor(
        product_id, customer_id, competitor_name, competitor_price
    )
    
    return jsonify(result)

@main_bp.route('/api/dynamic-pricing', methods=['POST'])
@login_required
def dynamic_pricing():
    """API endpoint for dynamic pricing recommendations"""
    data = request.get_json()
    
    product_id = data.get('product_id')
    customer_id = data.get('customer_id')
    
    if not product_id or not customer_id:
        return jsonify({'error': 'Product ID and Customer ID are required'}), 400
    
    result = pricing_service.get_dynamic_pricing_recommendations(product_id, customer_id)
    
    return jsonify(result)

@main_bp.route('/api/customer-churn-risk/<int:customer_id>')
@login_required
def customer_churn_risk(customer_id):
    """API endpoint for customer churn risk prediction"""
    result = ml_service.predict_customer_churn_risk(customer_id)
    return jsonify(result)

@main_bp.route('/api/ml-models/performance')
@login_required
def ml_models_performance():
    """API endpoint for ML models performance summary"""
    result = ml_service.get_model_performance_summary()
    return jsonify(result)

@main_bp.route('/api/ml-models/train-price-prediction', methods=['POST'])
@login_required
def train_price_prediction_model():
    """API endpoint for training price prediction model"""
    data = request.get_json()
    model_name = data.get('model_name', 'price_prediction_v1')
    
    result = ml_service.train_price_prediction_model(model_name)
    return jsonify(result)

@main_bp.route('/api/ml-models/train-churn-prediction', methods=['POST'])
@login_required
def train_churn_prediction_model():
    """API endpoint for training churn prediction model"""
    data = request.get_json()
    model_name = data.get('model_name', 'churn_prediction_v1')
    
    result = ml_service.train_customer_churn_model(model_name)
    return jsonify(result)

@main_bp.route('/customer-analytics')
@login_required
def customer_analytics():
    """Customer analytics dashboard"""
    # Get customer segments
    customers = Customer.query.all()
    segments = {}
    
    for customer in customers:
        analytics = CustomerAnalytics.query.filter_by(customer_id=customer.id).first()
        if analytics:
            segment = analytics.get_customer_segment()
            segments[segment] = segments.get(segment, 0) + 1
    
    # Get top customers by spending
    top_customers = Customer.query.order_by(Customer.total_spent.desc()).limit(10).all()
    
    # Get customers at risk
    at_risk_customers = db.session.query(Customer, CustomerAnalytics).join(
        CustomerAnalytics
    ).filter(CustomerAnalytics.churn_risk_score > 0.7).limit(10).all()
    
    return render_template('customer_analytics.html',
                         segments=segments,
                         top_customers=top_customers,
                         at_risk_customers=at_risk_customers)

@main_bp.route('/competitor-analysis')
@login_required
def competitor_analysis():
    """Competitor analysis dashboard"""
    from app.models import Competitor, CompetitorPrice
    
    competitors = Competitor.query.filter_by(is_active=True).all()
    
    # Get competitor pricing data
    competitor_data = []
    for competitor in competitors:
        prices = CompetitorPrice.query.filter_by(competitor_id=competitor.id).all()
        avg_price = sum(p.monthly_price for p in prices) / len(prices) if prices else 0
        
        competitor_data.append({
            'competitor': competitor,
            'avg_price': avg_price,
            'price_count': len(prices),
            'last_update': competitor.last_price_update
        })
    
    return render_template('competitor_analysis.html',
                         competitor_data=competitor_data) 