#to view users of my webpage
from app import app, db, User

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"User ID: {user.id}, Email: {user.email}, Google ID: {user.google_id}")