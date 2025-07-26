from flask import Blueprint, request, jsonify
from app import db
from app.models import Customer, Product, Order, CompetitorPrice
from app.services.pricing_service import PricingService
from app.services.ml_service import MLService
from datetime import datetime
import json

api_bp = Blueprint('api', __name__)
pricing_service = PricingService()
ml_service = MLService()

@api_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers"""
    customers = Customer.query.all()
    return jsonify([customer.to_dict() for customer in customers])

@api_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get specific customer"""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())

@api_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([product.to_dict() for product in products])

@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@api_bp.route('/pricing/optimal-price', methods=['POST'])
def get_optimal_price():
    """Get optimal price for customer and product"""
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

@api_bp.route('/pricing/competitor-prices', methods=['GET'])
def get_competitor_prices():
    """Get competitor prices for speed tier"""
    speed_tier = request.args.get('speed_tier')
    
    if not speed_tier:
        return jsonify({'error': 'Speed tier is required'}), 400
    
    prices = CompetitorPrice.query.filter_by(speed_tier=speed_tier).all()
    return jsonify([price.to_dict() for price in prices])

@api_bp.route('/ml/churn-risk/<int:customer_id>', methods=['GET'])
def get_churn_risk(customer_id):
    """Get customer churn risk prediction"""
    result = ml_service.predict_customer_churn_risk(customer_id)
    return jsonify(result)

@api_bp.route('/ml/price-prediction', methods=['POST'])
def predict_price():
    """Predict optimal price using ML"""
    data = request.get_json()
    
    product_id = data.get('product_id')
    customer_id = data.get('customer_id')
    
    if not product_id or not customer_id:
        return jsonify({'error': 'Product ID and Customer ID are required'}), 400
    
    result = ml_service.predict_optimal_price(product_id, customer_id)
    return jsonify(result)

@api_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

@api_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get specific order"""
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@api_bp.route('/analytics/customer/<int:customer_id>', methods=['GET'])
def get_customer_analytics(customer_id):
    """Get customer analytics"""
    from app.models import CustomerAnalytics
    
    analytics = CustomerAnalytics.query.filter_by(customer_id=customer_id).first()
    if not analytics:
        return jsonify({'error': 'Customer analytics not found'}), 404
    
    return jsonify(analytics.to_dict())

@api_bp.route('/analytics/order/<int:order_id>', methods=['GET'])
def get_order_analytics(order_id):
    """Get order analytics"""
    from app.models import OrderAnalytics
    
    analytics = OrderAnalytics.query.filter_by(order_id=order_id).first()
    if not analytics:
        return jsonify({'error': 'Order analytics not found'}), 404
    
    return jsonify(analytics.to_dict()) 