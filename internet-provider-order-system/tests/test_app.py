from app import create_app, db
from app.models import User


def test_login_and_dashboard():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with app.app_context():
        user = User(username='demo', email='demo@example.test', role='agent')
        user.set_password('test-only-password')
        db.session.add(user)
        db.session.commit()
    client = app.test_client()
    assert client.get('/login').status_code == 200
    assert client.get('/').status_code == 302
    assert client.get('/api/customers').status_code == 401
    assert client.post('/login', data={'username': 'demo', 'password': 'test-only-password'}).status_code == 400
    with client.session_transaction() as session:
        session['_user_id'] = '1'
        session['_fresh'] = True
    assert client.get('/api/products').status_code == 200
    assert client.get('/').status_code == 200
