from app import db
from app.models import Customer, CustomerAnalytics, Order, OrderItem
from datetime import datetime, timedelta
import pandas as pd

class CustomerService:
    def __init__(self):
        pass
    
    def get_customer_by_id(self, customer_id):
        """Get customer by ID"""
        return Customer.query.get(customer_id)
    
    def get_all_customers(self):
        """Get all customers"""
        return Customer.query.all()
    
    def create_customer(self, data):
        """Create a new customer"""
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            address=data['address'],
            customer_type=data.get('customer_type', 'residential'),
            credit_score=data.get('credit_score', 700),
            income_level=data.get('income_level', 'medium')
        )
        db.session.add(customer)
        db.session.commit()
        return customer
    
    def update_customer(self, customer_id, data):
        """Update customer information"""
        customer = self.get_customer_by_id(customer_id)
        if customer:
            for key, value in data.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            db.session.commit()
        return customer
    
    def get_customer_analytics(self, customer_id):
        """Get customer analytics"""
        return CustomerAnalytics.query.filter_by(customer_id=customer_id).first()
    
    def calculate_customer_lifetime_value(self, customer_id):
        """Calculate customer lifetime value"""
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            return 0
        
        # Get all orders for the customer
        orders = Order.query.filter_by(customer_id=customer_id).all()
        total_spent = sum(order.total_amount for order in orders)
        
        # Calculate average order value
        avg_order_value = total_spent / len(orders) if orders else 0
        
        # Estimate future value based on customer segment
        if customer.customer_segment == 'premium':
            multiplier = 2.5
        elif customer.customer_segment == 'standard':
            multiplier = 1.5
        else:
            multiplier = 1.0
        
        return total_spent * multiplier
    
    def get_customer_order_history(self, customer_id):
        """Get customer order history"""
        return Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    
    def get_customer_segment(self, customer_id):
        """Get customer segment based on behavior"""
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            return 'unknown'
        
        analytics = self.get_customer_analytics(customer_id)
        if not analytics:
            return customer.customer_segment
        
        # Determine segment based on analytics
        if analytics.total_spent > 5000 and analytics.loyalty_score > 0.8:
            return 'premium'
        elif analytics.total_spent > 2000 and analytics.loyalty_score > 0.6:
            return 'standard'
        elif analytics.churn_risk > 0.7:
            return 'at-risk'
        else:
            return 'basic'
    
    def update_customer_analytics(self, customer_id):
        """Update customer analytics"""
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            return None
        
        orders = Order.query.filter_by(customer_id=customer_id).all()
        total_orders = len(orders)
        total_spent = sum(order.total_amount for order in orders)
        
        # Calculate loyalty score
        loyalty_score = min(1.0, total_orders / 10.0)  # Max loyalty at 10+ orders
        
        # Calculate price sensitivity
        price_sensitivity = 0.5  # Default value, could be calculated from order history
        
        # Calculate churn risk
        recent_orders = [o for o in orders if o.created_at > datetime.now() - timedelta(days=90)]
        if total_orders > 0 and len(recent_orders) == 0:
            churn_risk = 0.9  # High risk if no recent orders
        elif total_orders > 0:
            churn_risk = 1.0 - (len(recent_orders) / total_orders)
        else:
            churn_risk = 0.5
        
        # Update or create analytics
        analytics = self.get_customer_analytics(customer_id)
        if not analytics:
            analytics = CustomerAnalytics(customer_id=customer_id)
            db.session.add(analytics)
        
        analytics.total_orders = total_orders
        analytics.total_spent = total_spent
        analytics.loyalty_score = loyalty_score
        analytics.price_sensitivity = price_sensitivity
        analytics.churn_risk = churn_risk
        analytics.last_updated = datetime.now()
        
        db.session.commit()
        return analytics
