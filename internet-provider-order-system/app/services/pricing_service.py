from app import db
from app.models import Product, Customer, CompetitorPrice, PriceHistory, CustomerAnalytics
from app.services.ml_service import MLService
from datetime import datetime, timedelta
import numpy as np

class PricingService:
    def __init__(self):
        self.ml_service = MLService()
    
    def get_optimal_price_for_customer(self, product_id, customer_id, competitor_name=None):
        """Get optimal price for a specific customer and product"""
        product = Product.query.get(product_id)
        customer = Customer.query.get(customer_id)
        
        if not product or not customer:
            return {'error': 'Product or customer not found'}
        
        # Get customer analytics
        analytics = CustomerAnalytics.query.filter_by(customer_id=customer_id).first()
        
        # Get competitor prices
        competitor_prices = self.get_competitor_prices(product.get_speed_tier(), competitor_name)
        
        # Get ML prediction
        ml_prediction = self.ml_service.predict_optimal_price(product_id, customer_id, competitor_prices)
        
        if 'error' in ml_prediction:
            # Fallback to rule-based pricing
            return self.get_rule_based_price(product, customer, analytics, competitor_prices)
        
        # Apply customer-specific adjustments
        final_price = self.apply_customer_adjustments(
            ml_prediction['optimal_price'], 
            customer, 
            analytics, 
            competitor_prices
        )
        
        # Get price justification
        justification = self.get_price_justification(
            product, customer, analytics, competitor_prices, final_price
        )
        
        return {
            'product_id': product_id,
            'customer_id': customer_id,
            'base_price': product.base_price,
            'ml_predicted_price': ml_prediction['optimal_price'],
            'final_price': final_price,
            'discount_percentage': ((product.base_price - final_price) / product.base_price) * 100,
            'competitor_comparison': self.get_competitor_comparison(competitor_prices, final_price),
            'justification': justification,
            'confidence_score': ml_prediction['confidence_score'],
            'factors': ml_prediction['factors']
        }
    
    def get_rule_based_price(self, product, customer, analytics, competitor_prices):
        """Fallback rule-based pricing when ML model is not available"""
        base_price = product.base_price
        customer_tier = customer.get_pricing_tier()
        
        # Base tier adjustments
        if customer_tier == 'tier_1':
            base_price *= 0.85  # 15% discount for premium customers
        elif customer_tier == 'tier_2':
            base_price *= 0.90  # 10% discount for standard customers
        
        # Competitor price matching
        if competitor_prices:
            avg_competitor_price = np.mean([cp.get_effective_price() for cp in competitor_prices])
            if avg_competitor_price < base_price:
                # Match competitor price with small margin
                base_price = avg_competitor_price * 0.95
        
        # Customer loyalty adjustments
        if analytics and analytics.loyalty_score > 0.8:
            base_price *= 0.95  # Additional 5% for very loyal customers
        
        # Price sensitivity adjustments
        if analytics and analytics.price_sensitivity_score > 0.7:
            base_price *= 0.90  # Additional 10% for price-sensitive customers
        
        return {
            'product_id': product.id,
            'customer_id': customer.id,
            'base_price': product.base_price,
            'final_price': base_price,
            'discount_percentage': ((product.base_price - base_price) / product.base_price) * 100,
            'pricing_method': 'rule_based',
            'confidence_score': 0.7
        }
    
    def apply_customer_adjustments(self, base_price, customer, analytics, competitor_prices):
        """Apply customer-specific price adjustments"""
        adjusted_price = base_price
        
        # Customer segment adjustments
        segment = customer.get_customer_segment()
        if segment == 'premium':
            adjusted_price *= 0.95  # Premium customers get better pricing
        elif segment == 'at_risk':
            adjusted_price *= 0.90  # At-risk customers get aggressive pricing
        
        # Historical behavior adjustments
        if analytics:
            # Price sensitivity
            if analytics.price_sensitivity_score > 0.8:
                adjusted_price *= 0.85  # Very price-sensitive customers
            
            # Loyalty rewards
            if analytics.loyalty_score > 0.9:
                adjusted_price *= 0.90  # Very loyal customers
            
            # Churn risk mitigation
            if analytics.churn_risk_score > 0.7:
                adjusted_price *= 0.80  # High churn risk customers
        
        # Competitor pressure adjustments
        if competitor_prices:
            avg_competitor = np.mean([cp.get_effective_price() for cp in competitor_prices])
            if avg_competitor < adjusted_price * 0.9:  # Competitor is significantly cheaper
                adjusted_price = avg_competitor * 0.95  # Beat competitor by 5%
        
        return adjusted_price
    
    def get_competitor_prices(self, speed_tier, competitor_name=None):
        """Get competitor prices for a specific speed tier"""
        query = CompetitorPrice.query.filter_by(speed_tier=speed_tier)
        
        if competitor_name:
            query = query.join(Competitor).filter(Competitor.name == competitor_name)
        
        return query.all()
    
    def get_competitor_comparison(self, competitor_prices, our_price):
        """Compare our price with competitor prices"""
        if not competitor_prices:
            return {'status': 'no_competitor_data'}
        
        competitor_prices_list = [cp.get_effective_price() for cp in competitor_prices]
        avg_competitor = np.mean(competitor_prices_list)
        min_competitor = min(competitor_prices_list)
        max_competitor = max(competitor_prices_list)
        
        price_difference = ((our_price - avg_competitor) / avg_competitor) * 100
        
        if price_difference <= -10:
            status = 'significantly_cheaper'
        elif price_difference <= -5:
            status = 'cheaper'
        elif price_difference <= 5:
            status = 'competitive'
        elif price_difference <= 15:
            status = 'more_expensive'
        else:
            status = 'significantly_more_expensive'
        
        return {
            'status': status,
            'our_price': our_price,
            'avg_competitor_price': avg_competitor,
            'min_competitor_price': min_competitor,
            'max_competitor_price': max_competitor,
            'price_difference_percentage': price_difference,
            'competitor_count': len(competitor_prices)
        }
    
    def get_price_justification(self, product, customer, analytics, competitor_prices, final_price):
        """Generate price justification for the customer"""
        justification = []
        
        # Base price reference
        justification.append(f"Base price: ${product.base_price:.2f}")
        
        # Customer tier benefits
        tier = customer.get_pricing_tier()
        if tier == 'tier_1':
            justification.append("Premium customer discount applied")
        elif tier == 'tier_2':
            justification.append("Standard customer discount applied")
        
        # Competitor matching
        if competitor_prices:
            comparison = self.get_competitor_comparison(competitor_prices, final_price)
            if comparison['status'] in ['significantly_cheaper', 'cheaper']:
                justification.append("Competitive pricing to match market rates")
            elif comparison['status'] == 'competitive':
                justification.append("Competitive market pricing")
        
        # Customer-specific factors
        if analytics:
            if analytics.loyalty_score > 0.8:
                justification.append("Loyalty reward discount")
            
            if analytics.price_sensitivity_score > 0.7:
                justification.append("Price sensitivity consideration")
            
            if analytics.churn_risk_score > 0.6:
                justification.append("Retention pricing applied")
        
        # Final price summary
        discount = ((product.base_price - final_price) / product.base_price) * 100
        if discount > 0:
            justification.append(f"Total savings: {discount:.1f}% off base price")
        
        return justification
    
    def price_match_competitor(self, product_id, customer_id, competitor_name, competitor_price):
        """Price match a specific competitor offer"""
        product = Product.query.get(product_id)
        customer = Customer.query.get(customer_id)
        
        if not product or not customer:
            return {'error': 'Product or customer not found'}
        
        # Validate competitor price
        if competitor_price <= 0:
            return {'error': 'Invalid competitor price'}
        
        # Calculate our matching price (slightly better than competitor)
        matching_price = competitor_price * 0.98  # 2% better than competitor
        
        # Apply minimum margin protection
        min_price = product.base_price * 0.7  # Minimum 30% discount
        final_price = max(matching_price, min_price)
        
        # Create price history record
        price_history = PriceHistory(
            product_id=product_id,
            base_price=product.base_price,
            effective_price=final_price,
            price_change_type='price_match',
            price_change_reason=f'Price match with {competitor_name}',
            competitor_avg_price=competitor_price
        )
        
        db.session.add(price_history)
        db.session.commit()
        
        return {
            'product_id': product_id,
            'customer_id': customer_id,
            'competitor_name': competitor_name,
            'competitor_price': competitor_price,
            'our_price': final_price,
            'savings_percentage': ((product.base_price - final_price) / product.base_price) * 100,
            'price_match_guarantee': True
        }
    
    def get_dynamic_pricing_recommendations(self, product_id, customer_id):
        """Get dynamic pricing recommendations based on customer behavior"""
        product = Product.query.get(product_id)
        customer = Customer.query.get(customer_id)
        analytics = CustomerAnalytics.query.filter_by(customer_id=customer_id).first()
        
        if not product or not customer:
            return {'error': 'Product or customer not found'}
        
        recommendations = []
        
        # Churn prevention pricing
        if analytics and analytics.churn_risk_score > 0.7:
            recommendations.append({
                'type': 'churn_prevention',
                'discount_percentage': 15,
                'reason': 'High churn risk customer - retention pricing',
                'priority': 'high'
            })
        
        # Loyalty rewards
        if analytics and analytics.loyalty_score > 0.8:
            recommendations.append({
                'type': 'loyalty_reward',
                'discount_percentage': 10,
                'reason': 'Loyal customer reward',
                'priority': 'medium'
            })
        
        # Price sensitivity accommodation
        if analytics and analytics.price_sensitivity_score > 0.8:
            recommendations.append({
                'type': 'price_sensitivity',
                'discount_percentage': 12,
                'reason': 'Price-sensitive customer accommodation',
                'priority': 'high'
            })
        
        # Competitor pressure response
        competitor_prices = self.get_competitor_prices(product.get_speed_tier())
        if competitor_prices:
            avg_competitor = np.mean([cp.get_effective_price() for cp in competitor_prices])
            if avg_competitor < product.base_price * 0.9:
                recommendations.append({
                    'type': 'competitor_match',
                    'discount_percentage': 8,
                    'reason': 'Competitive market pricing',
                    'priority': 'high'
                })
        
        # Seasonal promotions
        current_month = datetime.now().month
        if current_month in [11, 12]:  # Holiday season
            recommendations.append({
                'type': 'seasonal',
                'discount_percentage': 5,
                'reason': 'Holiday season promotion',
                'priority': 'medium'
            })
        
        return {
            'product_id': product_id,
            'customer_id': customer_id,
            'base_price': product.base_price,
            'recommendations': recommendations,
            'total_possible_discount': sum(r['discount_percentage'] for r in recommendations)
        }
    
    def apply_negotiated_price(self, order_id, negotiated_price, reason, competitor_name=None):
        """Apply negotiated price to an order"""
        order = Order.query.get(order_id)
        
        if not order:
            return {'error': 'Order not found'}
        
        # Validate negotiated price
        if negotiated_price <= 0:
            return {'error': 'Invalid negotiated price'}
        
        # Apply negotiated price
        order.set_negotiated_price(negotiated_price, competitor_name)
        
        # Update order items with negotiated pricing
        for item in order.items:
            # Calculate proportional discount
            original_total = item.total_price
            discount_ratio = negotiated_price / order.subtotal
            new_item_price = original_total * discount_ratio
            item.unit_price = new_item_price / item.quantity
            item.calculate_total()
        
        # Recalculate order totals
        order.calculate_totals()
        
        # Add price history record
        for item in order.items:
            price_history = PriceHistory(
                product_id=item.product_id,
                base_price=item.product.base_price,
                effective_price=item.unit_price,
                price_change_type='negotiated',
                price_change_reason=reason,
                competitor_avg_price=0  # Will be updated if competitor info available
            )
            db.session.add(price_history)
        
        db.session.commit()
        
        return {
            'order_id': order_id,
            'original_total': order.subtotal,
            'negotiated_total': negotiated_price,
            'savings': order.subtotal - negotiated_price,
            'savings_percentage': ((order.subtotal - negotiated_price) / order.subtotal) * 100,
            'reason': reason
        } 