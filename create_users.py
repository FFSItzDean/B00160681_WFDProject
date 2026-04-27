"""
Script to create users with proper password hashing
Run this after migrations: python create_users.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from supply_chain.models import User

def create_users():
    """Create all test users with password 'password'"""
    users_data = [
        {'username': 'admin', 'email': 'admin@admin.com', 'role': 'ADMIN', 
         'first_name': 'Admin', 'last_name': 'User', 'is_staff': True, 'is_superuser': True},
        {'username': 'supplier1', 'email': 'supplier1@supplier.com', 'role': 'SUPPLIER',
         'first_name': 'John', 'last_name': 'Supplier'},
        {'username': 'manager1', 'email': 'manager1@restaurant.com', 'role': 'MANAGER',
         'first_name': 'Mary', 'last_name': 'Manager'},
        {'username': 'warehouse1', 'email': 'warehouse1@warehouse.com', 'role': 'WAREHOUSE',
         'first_name': 'Bob', 'last_name': 'Warehouse'},
        {'username': 'driver1', 'email': 'driver1@delivery.com', 'role': 'DRIVER',
         'first_name': 'Tom', 'last_name': 'Driver'},
        {'username': 'accountant1', 'email': 'accountant1@accounting.com', 'role': 'ACCOUNTANT',
         'first_name': 'Alice', 'last_name': 'Accountant'},
    ]
    
    for user_data in users_data:
        username = user_data['username']
        if User.objects.filter(username=username).exists():
            print(f"User {username} already exists, skipping...")
            continue
        
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password='password',
            role=user_data['role'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone='123-456-7890'
        )
        
        if user_data.get('is_staff'):
            user.is_staff = True
        if user_data.get('is_superuser'):
            user.is_superuser = True
        user.save()
        
        print(f"Created user: {username} ({user_data['role']})")
    
    print("\nAll users created successfully!")
    print("Password for all users: password")

if __name__ == '__main__':
    create_users()
