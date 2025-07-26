# Internet Provider Order Entry System

A comprehensive order management system for internet service providers with advanced predictive pricing models, competitor analysis, and customer behavior analytics.

## Features

### 🎯 Core Functionality
- **Order Management**: Complete order lifecycle from creation to completion
- **Customer Management**: Comprehensive customer profiles with segmentation
- **Product Catalog**: Internet service products with pricing tiers
- **User Management**: Role-based access control (Admin, Manager, Agent)

### 🤖 AI/ML Capabilities
- **Predictive Pricing**: ML models for optimal price recommendations
- **Churn Prediction**: Customer churn risk analysis and prevention
- **Competitor Analysis**: Real-time competitor price tracking and matching
- **Dynamic Pricing**: Customer-specific pricing based on behavior and history

### 📊 Analytics & Insights
- **Customer Analytics**: Lifetime value, loyalty scores, price sensitivity
- **Order Analytics**: Conversion rates, profitability analysis
- **Market Intelligence**: Competitor positioning and market trends
- **Performance Metrics**: Revenue tracking and business intelligence

### 💰 Pricing Optimization
- **Price Matching**: Automatic competitor price matching
- **Negotiation Support**: Tools for price negotiation with customers
- **Promotional Pricing**: Dynamic promotional offers and discounts
- **Tier-based Pricing**: Customer segment-specific pricing strategies

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite (production-ready for PostgreSQL/MySQL)
- **ML/AI**: Scikit-learn, XGBoost, LightGBM
- **Frontend**: HTML/CSS/JavaScript (Bootstrap for UI)
- **Authentication**: Flask-Login with JWT tokens
- **Data Processing**: Pandas, NumPy

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd internet-provider-order-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   - Open browser and go to `http://localhost:5000`
   - Default admin credentials: admin/admin123

## Project Structure

```
internet-provider-order-system/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── user.py             # User authentication
│   │   ├── customer.py         # Customer management
│   │   ├── product.py          # Product catalog
│   │   ├── order.py            # Order management
│   │   ├── competitor.py       # Competitor tracking
│   │   ├── pricing.py          # Pricing models
│   │   └── analytics.py        # Analytics models
│   ├── services/               # Business logic
│   │   ├── ml_service.py       # ML/AI services
│   │   ├── pricing_service.py  # Pricing optimization
│   │   ├── customer_service.py # Customer management
│   │   └── order_service.py    # Order processing
│   ├── views/                  # Web routes
│   │   ├── main.py            # Dashboard & main views
│   │   ├── auth.py            # Authentication
│   │   ├── orders.py          # Order management
│   │   ├── admin.py           # Admin functions
│   │   └── api.py             # API endpoints
│   ├── templates/             # HTML templates
│   └── static/                # CSS, JS, images
├── ml_models/                 # Trained ML models
├── data/                      # Sample data
├── config/                    # Configuration files
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
├── run.py                     # Application entry point
└── README.md                  # This file
```

## Key Features Explained

### 1. Predictive Pricing Model

The system uses machine learning to predict optimal pricing based on:
- Customer historical behavior
- Competitor pricing
- Market demand
- Customer segmentation
- Price sensitivity analysis

```python
# Example usage
pricing_result = pricing_service.get_optimal_price_for_customer(
    product_id=1, 
    customer_id=123,
    competitor_name="Competitor A"
)
```

### 2. Customer Churn Prediction

ML models analyze customer behavior to predict churn risk:
- Purchase history analysis
- Service usage patterns
- Price sensitivity scoring
- Customer satisfaction metrics

```python
# Get churn risk for customer
churn_analysis = ml_service.predict_customer_churn_risk(customer_id=123)
```

### 3. Competitor Price Matching

Automatic competitor price tracking and matching:
- Real-time competitor price monitoring
- Price matching algorithms
- Market positioning analysis
- Competitive intelligence

### 4. Dynamic Pricing Recommendations

Customer-specific pricing strategies:
- Loyalty-based discounts
- Retention pricing for at-risk customers
- Seasonal promotions
- Market-driven adjustments

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /register` - User registration

### Orders
- `GET /orders` - List all orders
- `POST /orders/new` - Create new order
- `GET /orders/<id>` - Get order details
- `PUT /orders/<id>` - Update order
- `POST /orders/<id>/negotiate` - Price negotiation

### Pricing
- `POST /api/optimal-price` - Get optimal price
- `POST /api/price-match` - Price matching
- `POST /api/dynamic-pricing` - Dynamic pricing recommendations

### Analytics
- `GET /api/customer-churn-risk/<id>` - Customer churn analysis
- `GET /api/ml-models/performance` - ML model performance
- `GET /api/order-analytics` - Order analytics data

## Database Schema

### Core Tables
- **users** - System users and authentication
- **customers** - Customer profiles and segmentation
- **products** - Internet service products
- **orders** - Order management
- **order_items** - Order line items
- **competitors** - Competitor information
- **competitor_prices** - Competitor pricing data
- **pricing_models** - ML model metadata
- **price_history** - Historical pricing data
- **customer_analytics** - Customer behavior analytics
- **order_analytics** - Order performance analytics

## ML Models

### 1. Price Prediction Model
- **Type**: Random Forest Regression
- **Features**: Base price, competitor prices, market demand, customer segment
- **Output**: Optimal price recommendation

### 2. Churn Prediction Model
- **Type**: Random Forest Classification
- **Features**: Customer behavior, spending patterns, service usage
- **Output**: Churn risk probability

### 3. Customer Segmentation
- **Type**: Rule-based + ML clustering
- **Features**: Spending, loyalty, price sensitivity
- **Output**: Customer segments (VIP, Loyal, At-risk, etc.)

## Configuration

### Environment Variables
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///internet_provider.db
FLASK_ENV=development
DEBUG=True
```

### ML Model Configuration
```python
# ML model parameters
MODEL_CONFIG = {
    'price_prediction': {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    },
    'churn_prediction': {
        'n_estimators': 100,
        'class_weight': 'balanced',
        'random_state': 42
    }
}
```

## Usage Examples

### Creating an Order with Predictive Pricing

```python
from app.services.pricing_service import PricingService

pricing_service = PricingService()

# Get optimal price for customer
pricing_result = pricing_service.get_optimal_price_for_customer(
    product_id=1,
    customer_id=123
)

# Create order with optimized pricing
order = Order(
    customer_id=123,
    created_by_id=current_user.id
)

# Apply optimal pricing to order items
for item in order.items:
    optimal_price = pricing_service.get_optimal_price_for_customer(
        item.product_id, 
        order.customer_id
    )
    item.unit_price = optimal_price['final_price']
```

### Customer Churn Analysis

```python
from app.services.ml_service import MLService

ml_service = MLService()

# Analyze customer churn risk
churn_analysis = ml_service.predict_customer_churn_risk(customer_id=123)

if churn_analysis['churn_risk_score'] > 0.7:
    # Apply retention strategies
    retention_offers = get_retention_offers(customer_id=123)
    send_retention_campaign(customer_id=123, offers=retention_offers)
```

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific tests:
```bash
python -m pytest tests/test_pricing_service.py
python -m pytest tests/test_ml_service.py
```

## Deployment

### Production Deployment
1. Set up production database (PostgreSQL/MySQL)
2. Configure environment variables
3. Set up reverse proxy (Nginx)
4. Use production WSGI server (Gunicorn)
5. Set up monitoring and logging

### Docker Deployment
```bash
# Build Docker image
docker build -t internet-provider-system .

# Run container
docker run -p 5000:5000 internet-provider-system
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Roadmap

### Phase 1 (Current)
- ✅ Core order management
- ✅ Basic ML pricing models
- ✅ Customer analytics
- ✅ Competitor tracking

### Phase 2 (Next)
- 🔄 Advanced ML models
- 🔄 Real-time competitor monitoring
- 🔄 Automated price optimization
- 🔄 Advanced reporting

### Phase 3 (Future)
- 📋 AI-powered customer service
- 📋 Predictive maintenance
- 📋 Advanced market intelligence
- �� Mobile application 