#!/usr/bin/env python
"""
Script to add the 'role' column to the main_user table
This fixes the error: "Field 'role' doesn't have a default value"
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick_project.settings')
django.setup()

from django.db import connection

def add_role_column():
    """Add role column to main_user table"""
    try:
        with connection.cursor() as cursor:
            # Check if column already exists
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'main_user'
                AND COLUMN_NAME = 'role'
            """)

            column_exists = cursor.fetchone()[0] > 0

            if column_exists:
                print("Column 'role' already exists in main_user table!")
                return

            # Add the role column
            print("Adding 'role' column to main_user table...")
            cursor.execute("""
                ALTER TABLE main_user
                ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'
            """)

            print("Success! Column 'role' has been added to main_user table.")
            print("Default value: 'user'")
            print("\nYou can now create users with roles!")

    except Exception as e:
        print(f"Error adding role column: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_role_column()
