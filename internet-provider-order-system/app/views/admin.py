from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, Product, ProductCategory, Customer, Competitor, CompetitorPrice
from app.services.ml_service import MLService
from datetime import datetime
import json

admin_bp = Blueprint('admin', __name__)
ml_service = MLService()

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # System statistics
    total_users = User.query.count()
    total_customers = Customer.query.count()
    total_products = Product.query.count()
    total_competitors = Competitor.query.count()
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_customers=total_customers,
                         total_products=total_products,
                         total_competitors=total_competitors,
                         recent_users=recent_users,
                         recent_products=recent_products)

@admin_bp.route('/admin/users')
@login_required
def user_management():
    """User management"""
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create new user"""
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        role = data.get('role', 'agent')
        
        if not all([username, email, password, first_name, last_name]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully!', 'success')
        return jsonify({'success': True, 'user_id': user.id})
    
    return render_template('admin/create_user.html')

@admin_bp.route('/admin/products')
@login_required
def product_management():
    """Product management"""
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    products = Product.query.all()
    categories = ProductCategory.query.all()
    
    return render_template('admin/products.html',
                         products=products,
                         categories=categories)

@admin_bp.route('/admin/products/new', methods=['GET', 'POST'])
@login_required
def create_product():
    """Create new product"""
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description')
        category_id = data.get('category_id')
        internet_speed = data.get('internet_speed')
        base_price = data.get('base_price')
        
        if not all([name, category_id, base_price]):
            return jsonify({'error': 'Name, category, and base price are required'}), 400
        
        product = Product(
            name=name,
            description=description,
            category_id=category_id,
            internet_speed=internet_speed,
            base_price=base_price
        )
        
        # Set features if provided
        if data.get('features'):
            product.set_features_list(data['features'])
        
        # Set add-ons if provided
        if data.get('add_ons'):
            product.set_add_ons_list(data['add_ons'])
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product created successfully!', 'success')
        return jsonify({'success': True, 'product_id': product.id})
    
    categories = ProductCategory.query.all()
    return render_template('admin/create_product.html', categories=categories)

@admin_bp.route('/admin/competitors')
@login_required
def competitor_management():
    """Competitor management"""
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    competitors = Competitor.query.all()
    return render_template('admin/competitors.html', competitors=competitors)

@admin_bp.route('/admin/competitors/new', methods=['GET', 'POST'])
@login_required
def create_competitor():
    """Create new competitor"""
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        data = request.get_json()
        
        name = data.get('name')
        website = data.get('website')
        competitor_type = data.get('competitor_type', 'direct')
        
        if not name:
            return jsonify({'error': 'Competitor name is required'}), 400
        
        competitor = Competitor(
            name=name,
            website=website,
            competitor_type=competitor_type
        )
        
        # Set service areas if provided
        if data.get('service_areas'):
            competitor.set_service_areas_list(data['service_areas'])
        
        db.session.add(competitor)
        db.session.commit()
        
        flash('Competitor created successfully!', 'success')
        return jsonify({'success': True, 'competitor_id': competitor.id})
    
    return render_template('admin/create_competitor.html')

@admin_bp.route('/admin/ml-models')
@login_required
def ml_models():
    """ML models management"""
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    from app.models import PricingModel
    models = PricingModel.query.all()
    
    return render_template('admin/ml_models.html', models=models)

@admin_bp.route('/admin/ml-models/train-price-prediction', methods=['POST'])
@login_required
def train_price_prediction():
    """Train price prediction model"""
    if current_user.role not in ['admin', 'manager']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    model_name = data.get('model_name', 'price_prediction_v1')
    
    try:
        result = ml_service.train_price_prediction_model(model_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/ml-models/train-churn-prediction', methods=['POST'])
@login_required
def train_churn_prediction():
    """Train churn prediction model"""
    if current_user.role not in ['admin', 'manager']:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    model_name = data.get('model_name', 'churn_prediction_v1')
    
    try:
        result = ml_service.train_customer_churn_model(model_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/system-config')
@login_required
def system_config():
    """System configuration"""
    if current_user.role not in ['admin']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/system_config.html')

@admin_bp.route('/admin/data-import')
@login_required
def data_import():
    """Data import interface"""
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/data_import.html')

@admin_bp.route('/admin/reports')
@login_required
def reports():
    """Reports and analytics"""
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/reports.html') 