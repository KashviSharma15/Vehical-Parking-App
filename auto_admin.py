from .models import User
from .database import db

def create_auto_admin():
    existing_admin = User.query.filter_by(is_admin=True).first()
    if not existing_admin:
        admin = User(email='admin@admin',username='admin', password='admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("Admin got created")
    else:
        print("Admin already exists")
