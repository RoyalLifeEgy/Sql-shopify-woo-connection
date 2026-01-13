"""
Initialize database and create default admin user
"""
from database import init_db, SessionLocal
from models import User
from utils.security import get_password_hash
import sys


def create_admin_user(username: str = "admin", password: str = "admin", email: str = "admin@example.com"):
    """Create default admin user"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"User '{username}' already exists.")
            return

        # Create admin user
        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name="Administrator",
            is_active=True,
            is_superuser=True
        )

        db.add(admin)
        db.commit()
        print(f"Admin user created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Email: {email}")
        print("\nIMPORTANT: Please change the default password after first login!")

    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")

    print("\nCreating default admin user...")
    if len(sys.argv) > 3:
        create_admin_user(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) > 2:
        create_admin_user(sys.argv[1], sys.argv[2])
    else:
        create_admin_user()
