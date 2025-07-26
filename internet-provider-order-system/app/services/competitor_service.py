from app import db
from app.models import Competitor, CompetitorPrice, Product
from datetime import datetime, timedelta
import requests
import json

class CompetitorService:
    def __init__(self):
        pass
    
    def get_competitor_by_id(self, competitor_id):
        """Get competitor by ID"""
        return Competitor.query.get(competitor_id)
    
    def get_all_competitors(self):
        """Get all competitors"""
        return Competitor.query.all()
    
    def create_competitor(self, data):
        """Create a new competitor"""
        competitor = Competitor(
            name=data['name'],
            website=data['website'],
            market_position=data.get('market_position', 'standard'),
            service_areas=data.get('service_areas', []),
            notes=data.get('notes', '')
        )
        db.session.add(competitor)
        db.session.commit()
        return competitor
    
    def update_competitor(self, competitor_id, data):
        """Update competitor information"""
        competitor = self.get_competitor_by_id(competitor_id)
        if competitor:
            for key, value in data.items():
                if hasattr(competitor, key):
                    setattr(competitor, key, value)
            db.session.commit()
        return competitor
    
    def add_competitor_price(self, data):
        """Add competitor price information"""
        price = CompetitorPrice(
            competitor_id=data['competitor_id'],
            product_name=data['product_name'],
            speed_tier=data['speed_tier'],
            price=data['price'],
            contract_length=data.get('contract_length', 12),
            setup_fee=data.get('setup_fee', 0),
            promotional_price=data.get('promotional_price'),
            promotional_duration=data.get('promotional_duration'),
            notes=data.get('notes', '')
        )
        db.session.add(price)
        db.session.commit()
        return price
    
    def get_competitor_prices(self, competitor_id=None):
        """Get competitor prices"""
        if competitor_id:
            return CompetitorPrice.query.filter_by(competitor_id=competitor_id).all()
        return CompetitorPrice.query.all()
    
    def get_prices_for_speed_tier(self, speed_tier):
        """Get all competitor prices for a specific speed tier"""
        return CompetitorPrice.query.filter_by(speed_tier=speed_tier).all()
    
    def get_lowest_price_for_speed(self, speed_tier):
        """Get the lowest price for a specific speed tier"""
        prices = self.get_prices_for_speed_tier(speed_tier)
        if prices:
            return min(prices, key=lambda x: x.effective_price)
        return None
    
    def update_competitor_prices(self):
        """Update competitor prices (simulated API call)"""
        # This would typically involve calling external APIs
        # For now, we'll simulate price updates
        competitors = self.get_all_competitors()
        
        for competitor in competitors:
            # Simulate price changes
            prices = self.get_competitor_prices(competitor.id)
            for price in prices:
                # Random price adjustment (±5%)
                import random
                adjustment = random.uniform(-0.05, 0.05)
                price.price = price.price * (1 + adjustment)
                price.last_updated = datetime.now()
        
        db.session.commit()
        return True
    
    def get_market_analysis(self):
        """Get market analysis summary"""
        competitors = self.get_all_competitors()
        analysis = {
            'total_competitors': len(competitors),
            'price_ranges': {},
            'market_share_estimate': {}
        }
        
        # Analyze price ranges by speed tier
        speed_tiers = ['100Mbps', '500Mbps', '1Gbps', '2Gbps']
        for tier in speed_tiers:
            prices = self.get_prices_for_speed_tier(tier)
            if prices:
                price_list = [p.effective_price for p in prices]
                analysis['price_ranges'][tier] = {
                    'min': min(price_list),
                    'max': max(price_list),
                    'avg': sum(price_list) / len(price_list),
                    'count': len(price_list)
                }
        
        return analysis
    
    def get_competitive_intelligence(self, product_id):
        """Get competitive intelligence for a specific product"""
        product = Product.query.get(product_id)
        if not product:
            return None
        
        # Find similar products from competitors
        similar_prices = CompetitorPrice.query.filter(
            CompetitorPrice.speed_tier == product.speed_tier
        ).all()
        
        intelligence = {
            'product_id': product_id,
            'our_price': product.base_price,
            'competitor_prices': [],
            'price_position': 'unknown',
            'recommendations': []
        }
        
        if similar_prices:
            competitor_prices = [p.effective_price for p in similar_prices]
            avg_competitor_price = sum(competitor_prices) / len(competitor_prices)
            
            intelligence['competitor_prices'] = [
                {
                    'competitor': p.competitor.name,
                    'price': p.effective_price,
                    'contract_length': p.contract_length
                }
                for p in similar_prices
            ]
            
            # Determine price position
            if product.base_price < avg_competitor_price * 0.9:
                intelligence['price_position'] = 'competitive'
                intelligence['recommendations'].append('Consider raising prices slightly')
            elif product.base_price > avg_competitor_price * 1.1:
                intelligence['price_position'] = 'premium'
                intelligence['recommendations'].append('Consider price matching or highlighting value')
            else:
                intelligence['price_position'] = 'market_average'
                intelligence['recommendations'].append('Monitor competitor price changes')
        
        return intelligence
