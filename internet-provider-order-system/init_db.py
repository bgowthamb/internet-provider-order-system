#!/usr/bin/env python3
"""
Database initialization script for Internet Provider Order Entry System
Creates sample data for testing and demonstration
"""

from app import create_app, db
from app.models import (
    User, Customer, ProductCategory, Product, Competitor, CompetitorPrice,
    CustomerAnalytics, PriceHistory
)
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample data for the system"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("Creating sample data...")
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@internetprovider.com',
            first_name='System',
            last_name='Administrator',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Create regular user
        agent_user = User(
            username='agent',
            email='agent@internetprovider.com',
            first_name='John',
            last_name='Agent',
            role='agent'
        )
        agent_user.set_password('agent123')
        db.session.add(agent_user)
        
        # Create product categories
        categories = [
            ProductCategory(name='Residential Internet', description='Home internet services'),
            ProductCategory(name='Business Internet', description='Business internet services'),
            ProductCategory(name='Enterprise Internet', description='Enterprise-grade internet services')
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        
        # Create products
        products = [
            Product(
                name='Basic Home Internet',
                description='100 Mbps internet for basic home use',
                category_id=1,
                internet_speed=100,
                data_cap=None,  # Unlimited
                contract_length=12,
                base_price=49.99,
                promotional_price=39.99,
                promotional_duration=6,
                installation_fee=99.00,
                activation_fee=0.00
            ),
            Product(
                name='Standard Home Internet',
                description='500 Mbps internet for streaming and gaming',
                category_id=1,
                internet_speed=500,
                data_cap=None,
                contract_length=12,
                base_price=79.99,
                promotional_price=64.99,
                promotional_duration=6,
                installation_fee=99.00,
                activation_fee=0.00
            ),
            Product(
                name='Premium Home Internet',
                description='1 Gbps fiber internet for power users',
                category_id=1,
                internet_speed=1000,
                data_cap=None,
                contract_length=12,
                base_price=119.99,
                promotional_price=99.99,
                promotional_duration=6,
                installation_fee=0.00,
                activation_fee=0.00
            ),
            Product(
                name='Business Starter',
                description='200 Mbps business internet with static IP',
                category_id=2,
                internet_speed=200,
                data_cap=None,
                contract_length=24,
                base_price=149.99,
                installation_fee=199.00,
                activation_fee=50.00
            ),
            Product(
                name='Business Pro',
                description='500 Mbps business internet with advanced features',
                category_id=2,
                internet_speed=500,
                data_cap=None,
                contract_length=24,
                base_price=299.99,
                installation_fee=199.00,
                activation_fee=50.00
            )
        ]
        
        for product in products:
            # Set features
            if product.internet_speed >= 1000:
                features = ['Fiber optic connection', 'Unlimited data', 'Free installation', '24/7 support']
            elif product.internet_speed >= 500:
                features = ['High-speed connection', 'Unlimited data', 'Free modem', 'Technical support']
            else:
                features = ['Reliable connection', 'Unlimited data', 'Basic support']
            
            product.set_features_list(features)
            db.session.add(product)
        
        db.session.commit()
        
        # Create competitors
        competitors = [
            Competitor(
                name='Competitor A',
                website='https://competitora.com',
                competitor_type='direct',
                market_share=25.0,
                price_positioning='competitive',
                service_quality_rating=4.2,
                customer_satisfaction_score=4.0
            ),
            Competitor(
                name='Competitor B',
                website='https://competitorb.com',
                competitor_type='direct',
                market_share=30.0,
                price_positioning='premium',
                service_quality_rating=4.5,
                customer_satisfaction_score=4.3
            ),
            Competitor(
                name='Competitor C',
                website='https://competitorc.com',
                competitor_type='direct',
                market_share=20.0,
                price_positioning='budget',
                service_quality_rating=3.8,
                customer_satisfaction_score=3.7
            )
        ]
        
        for competitor in competitors:
            competitor.set_service_areas_list(['New York', 'Los Angeles', 'Chicago', 'Houston'])
            db.session.add(competitor)
        
        db.session.commit()
        
        # Create competitor prices
        competitor_prices = []
        speed_tiers = ['basic', 'standard', 'high_speed', 'gigabit']
        
        for competitor in competitors:
            for i, speed_tier in enumerate(speed_tiers):
                base_price = 40 + (i * 20)  # Base price varies by speed tier
                
                # Adjust price based on competitor positioning
                if competitor.price_positioning == 'premium':
                    price_multiplier = 1.2
                elif competitor.price_positioning == 'budget':
                    price_multiplier = 0.8
                else:
                    price_multiplier = 1.0
                
                monthly_price = base_price * price_multiplier
                
                cp = CompetitorPrice(
                    competitor_id=competitor.id,
                    speed_tier=speed_tier,
                    internet_speed=100 * (2 ** i),
                    monthly_price=monthly_price,
                    promotional_price=monthly_price * 0.8 if random.random() > 0.5 else None,
                    promotional_duration=6 if random.random() > 0.5 else None,
                    installation_fee=random.choice([0, 50, 99, 149]),
                    activation_fee=random.choice([0, 25, 50]),
                    contract_length=random.choice([12, 24]),
                    data_source='website',
                    confidence_score=0.9
                )
                
                features = ['Unlimited data', 'Free installation', '24/7 support']
                cp.set_features_list(features)
                competitor_prices.append(cp)
        
        for cp in competitor_prices:
            db.session.add(cp)
        
        db.session.commit()
        
        # Create customers with analytics
        customers = []
        for i in range(50):
            # Generate customer data
            first_name = f"Customer{i+1}"
            last_name = f"Smith{i+1}"
            email = f"customer{i+1}@example.com"
            
            # Random customer characteristics
            total_spent = random.uniform(500, 5000)
            avg_monthly_bill = random.uniform(50, 150)
            credit_score = random.randint(600, 800)
            household_size = random.randint(1, 6)
            
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                address=f"{random.randint(100, 9999)} Main St",
                city=random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
                state=random.choice(['NY', 'CA', 'IL', 'TX', 'AZ']),
                zip_code=f"{random.randint(10000, 99999)}",
                customer_type=random.choice(['residential', 'business']),
                credit_score=credit_score,
                income_level=random.choice(['low', 'medium', 'high']),
                household_size=household_size,
                total_spent=total_spent,
                avg_monthly_bill=avg_monthly_bill,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            
            db.session.add(customer)
            customers.append(customer)
        
        db.session.commit()
        
        # Create customer analytics
        for customer in customers:
            # Calculate analytics based on customer data
            customer_lifetime_days = (datetime.utcnow() - customer.created_at).days
            total_orders = random.randint(1, 10)
            avg_order_value = customer.total_spent / total_orders if total_orders > 0 else 0
            days_since_last_order = random.randint(1, 90)
            
            # Calculate loyalty score
            loyalty_score = min(1.0, (customer.total_spent / 5000) * 0.5 + (customer_lifetime_days / 365) * 0.3 + (1 / (days_since_last_order + 1)) * 0.2)
            
            # Calculate price sensitivity
            price_sensitivity_score = random.uniform(0.3, 0.9)
            
            # Calculate churn risk
            churn_risk_score = max(0.0, min(1.0, 
                (days_since_last_order / 90) * 0.4 + 
                (1 - loyalty_score) * 0.4 + 
                (price_sensitivity_score * 0.2)
            ))
            
            analytics = CustomerAnalytics(
                customer_id=customer.id,
                total_orders=total_orders,
                total_spent=customer.total_spent,
                avg_order_value=avg_order_value,
                first_order_date=customer.created_at,
                last_order_date=datetime.utcnow() - timedelta(days=days_since_last_order),
                customer_lifetime_days=customer_lifetime_days,
                days_since_last_order=days_since_last_order,
                order_frequency_days=customer_lifetime_days / total_orders if total_orders > 0 else 0,
                loyalty_score=loyalty_score,
                price_sensitivity_score=price_sensitivity_score,
                upgrade_probability=random.uniform(0.1, 0.8),
                churn_risk_score=churn_risk_score,
                promotional_response_rate=random.uniform(0.2, 0.9),
                discount_usage_frequency=random.uniform(0.1, 0.7),
                price_match_requests=random.randint(0, 5),
                preferred_contact_method=random.choice(['email', 'phone', 'sms']),
                response_rate_to_offers=random.uniform(0.3, 0.9)
            )
            
            db.session.add(analytics)
        
        db.session.commit()
        
        # Create price history
        for product in products:
            # Create historical price records
            for i in range(12):  # Last 12 months
                date = datetime.utcnow() - timedelta(days=30*i)
                
                # Simulate price changes
                price_change = random.uniform(-0.1, 0.1)  # ±10% change
                effective_price = product.base_price * (1 + price_change)
                
                # Get competitor average price for this period
                competitor_avg = sum(cp.monthly_price for cp in competitor_prices 
                                   if cp.speed_tier == product.get_speed_tier()) / len([cp for cp in competitor_prices if cp.speed_tier == product.get_speed_tier()])
                
                price_history = PriceHistory(
                    product_id=product.id,
                    base_price=product.base_price,
                    effective_price=effective_price,
                    price_change_type=random.choice(['increase', 'decrease', 'stable']),
                    price_change_reason=random.choice(['Market adjustment', 'Competitive response', 'Seasonal pricing']),
                    previous_price=product.base_price,
                    price_change_percentage=price_change * 100,
                    competitor_avg_price=competitor_avg,
                    market_demand_score=random.uniform(0.5, 1.0),
                    seasonality_factor=random.uniform(0.8, 1.2),
                    effective_date=date
                )
                
                db.session.add(price_history)
        
        db.session.commit()
        
        print("Sample data created successfully!")
        print(f"Created:")
        print(f"- {len(customers)} customers with analytics")
        print(f"- {len(products)} products")
        print(f"- {len(competitors)} competitors with pricing data")
        print(f"- Price history for all products")
        print(f"\nDefault login credentials:")
        print(f"Admin: admin/admin123")
        print(f"Agent: agent/agent123")

if __name__ == '__main__':
    create_sample_data() 