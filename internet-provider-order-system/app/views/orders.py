from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Customer, Product, Order, OrderItem, OrderAnalytics
from app.services.pricing_service import PricingService
from app.services.ml_service import MLService
from datetime import datetime, timedelta
import json

orders_bp = Blueprint('orders', __name__)
pricing_service = PricingService()
ml_service = MLService()

@orders_bp.route('/orders')
@login_required
def order_list():
    """List all orders"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Order.query
    
    if status_filter:
        query = query.filter(Order.order_status == status_filter)
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('orders/order_list.html', orders=orders, status_filter=status_filter)

@orders_bp.route('/orders/new', methods=['GET', 'POST'])
@login_required
def create_order():
    """Create new order"""
    if request.method == 'POST':
        data = request.get_json()
        
        customer_id = data.get('customer_id')
        products = data.get('products', [])
        
        if not customer_id or not products:
            return jsonify({'error': 'Customer ID and products are required'}), 400
        
        # Create order
        order = Order(
            customer_id=customer_id,
            created_by_id=current_user.id,
            order_type=data.get('order_type', 'new'),
            priority=data.get('priority', 'normal')
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Add order items
        total_amount = 0
        for product_data in products:
            product_id = product_data.get('product_id')
            quantity = product_data.get('quantity', 1)
            
            product = Product.query.get(product_id)
            if not product:
                continue
            
            # Get optimal price for this customer and product
            pricing_result = pricing_service.get_optimal_price_for_customer(
                product_id, customer_id
            )
            
            if 'error' in pricing_result:
                unit_price = product.base_price
            else:
                unit_price = pricing_result['final_price']
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=unit_price * quantity
            )
            
            db.session.add(order_item)
            total_amount += order_item.total_price
        
        # Calculate order totals
        order.calculate_totals()
        
        # Create order analytics
        analytics = OrderAnalytics(
            order_id=order.id,
            conversion_score=0.8,  # Default value
            profitability_score=0.7,  # Default value
            price_competitiveness_score=0.8  # Default value
        )
        
        db.session.add(analytics)
        db.session.commit()
        
        flash('Order created successfully!', 'success')
        return jsonify({
            'success': True,
            'order_id': order.id,
            'order_number': order.order_number,
            'total_amount': order.total_amount
        })
    
    # GET request - show form
    customers = Customer.query.all()
    products = Product.query.filter_by(is_active=True).all()
    
    return render_template('orders/create_order.html',
                         customers=customers,
                         products=products)

@orders_bp.route('/orders/<int:order_id>')
@login_required
def view_order(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    analytics = OrderAnalytics.query.filter_by(order_id=order_id).first()
    
    return render_template('orders/view_order.html',
                         order=order,
                         analytics=analytics)

@orders_bp.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    """Edit order"""
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Update order details
        order.order_status = data.get('order_status', order.order_status)
        order.priority = data.get('priority', order.priority)
        order.installation_date = datetime.fromisoformat(data['installation_date']) if data.get('installation_date') else None
        order.special_instructions = data.get('special_instructions', order.special_instructions)
        
        db.session.commit()
        
        flash('Order updated successfully!', 'success')
        return jsonify({'success': True})
    
    # GET request - show form
    customers = Customer.query.all()
    products = Product.query.filter_by(is_active=True).all()
    
    return render_template('orders/edit_order.html',
                         order=order,
                         customers=customers,
                         products=products)

@orders_bp.route('/orders/<int:order_id>/negotiate', methods=['POST'])
@login_required
def negotiate_price(order_id):
    """Negotiate price for an order"""
    data = request.get_json()
    
    negotiated_price = data.get('negotiated_price')
    reason = data.get('reason', 'Manual negotiation')
    competitor_name = data.get('competitor_name')
    
    if not negotiated_price:
        return jsonify({'error': 'Negotiated price is required'}), 400
    
    result = pricing_service.apply_negotiated_price(
        order_id, negotiated_price, reason, competitor_name
    )
    
    if 'error' in result:
        return jsonify(result), 400
    
    flash('Price negotiation applied successfully!', 'success')
    return jsonify(result)

@orders_bp.route('/api/order-pricing/<int:order_id>')
@login_required
def get_order_pricing(order_id):
    """Get pricing analysis for an order"""
    order = Order.query.get_or_404(order_id)
    
    pricing_analysis = []
    
    for item in order.items:
        # Get optimal pricing for each item
        pricing_result = pricing_service.get_optimal_price_for_customer(
            item.product_id, order.customer_id
        )
        
        if 'error' not in pricing_result:
            pricing_analysis.append({
                'product_id': item.product_id,
                'product_name': item.product.name,
                'current_price': item.unit_price,
                'optimal_price': pricing_result['final_price'],
                'potential_savings': item.unit_price - pricing_result['final_price'],
                'competitor_comparison': pricing_result['competitor_comparison'],
                'justification': pricing_result['justification']
            })
    
    return jsonify({
        'order_id': order_id,
        'current_total': order.total_amount,
        'pricing_analysis': pricing_analysis
    })

@orders_bp.route('/api/order-recommendations/<int:order_id>')
@login_required
def get_order_recommendations(order_id):
    """Get recommendations for an order"""
    order = Order.query.get_or_404(order_id)
    
    recommendations = []
    
    # Check customer churn risk
    churn_result = ml_service.predict_customer_churn_risk(order.customer_id)
    if 'error' not in churn_result and churn_result['churn_risk_score'] > 0.7:
        recommendations.append({
            'type': 'churn_prevention',
            'priority': 'high',
            'message': f"Customer has {churn_result['churn_risk_score']:.1%} churn risk. Consider retention offers.",
            'actions': churn_result.get('recommendations', [])
        })
    
    # Check for better pricing opportunities
    for item in order.items:
        pricing_result = pricing_service.get_dynamic_pricing_recommendations(
            item.product_id, order.customer_id
        )
        
        if 'error' not in pricing_result and pricing_result['recommendations']:
            recommendations.append({
                'type': 'pricing_optimization',
                'priority': 'medium',
                'message': f"Pricing optimization available for {item.product.name}",
                'recommendations': pricing_result['recommendations']
            })
    
    return jsonify({
        'order_id': order_id,
        'recommendations': recommendations
    })

@orders_bp.route('/orders/<int:order_id>/confirm')
@login_required
def confirm_order(order_id):
    """Confirm an order"""
    order = Order.query.get_or_404(order_id)
    
    if order.order_status == 'pending':
        order.order_status = 'confirmed'
        order.confirmed_at = datetime.utcnow()
        db.session.commit()
        
        flash('Order confirmed successfully!', 'success')
    else:
        flash('Order cannot be confirmed in current status', 'error')
    
    return redirect(url_for('orders.view_order', order_id=order_id))

@orders_bp.route('/orders/<int:order_id>/cancel')
@login_required
def cancel_order(order_id):
    """Cancel an order"""
    order = Order.query.get_or_404(order_id)
    
    if order.order_status in ['pending', 'confirmed']:
        order.order_status = 'cancelled'
        db.session.commit()
        
        flash('Order cancelled successfully!', 'success')
    else:
        flash('Order cannot be cancelled in current status', 'error')
    
    return redirect(url_for('orders.view_order', order_id=order_id))

@orders_bp.route('/api/order-analytics')
@login_required
def order_analytics():
    """Get order analytics data"""
    # Order status distribution
    status_counts = db.session.query(
        Order.order_status, db.func.count(Order.id)
    ).group_by(Order.order_status).all()
    
    # Revenue by month (last 12 months)
    monthly_revenue = []
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.created_at >= month_start,
            Order.created_at <= month_end
        ).scalar() or 0
        
        monthly_revenue.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': revenue
        })
    
    # Average order value
    avg_order_value = db.session.query(db.func.avg(Order.total_amount)).scalar() or 0
    
    return jsonify({
        'status_distribution': dict(status_counts),
        'monthly_revenue': monthly_revenue,
        'avg_order_value': avg_order_value
    }) 