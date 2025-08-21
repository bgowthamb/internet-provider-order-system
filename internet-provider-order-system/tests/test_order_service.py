import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Customer, Product, ProductCategory, Order
from app.services.order_service import OrderService


def setup_app():
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    app = create_app()
    app.testing = True
    return app


def test_create_and_update_order_status():
    app = setup_app()
    with app.app_context():
        user = User(username='agent', email='agent@example.com')
        user.set_password('password')
        customer = Customer(first_name='John', last_name='Doe', email='john@example.com')
        category = ProductCategory(name='Internet')
        product = Product(name='Basic Plan', base_price=50.0, category=category)
        db.session.add_all([user, customer, category, product])
        db.session.commit()

        service = OrderService()
        order_data = {
            'customer_id': customer.id,
            'created_by': user.id,
            'items': [
                {'product_id': product.id, 'quantity': 1}
            ]
        }

        order = service.create_order(order_data)
        assert order.order_status == 'pending'
        assert order.created_by_id == user.id

        service.update_order_status(order.id, 'confirmed')
        updated = service.get_order_by_id(order.id)
        assert updated.order_status == 'confirmed'

        confirmed_orders = service.get_orders_by_status('confirmed')
        assert order.id in [o.id for o in confirmed_orders]
