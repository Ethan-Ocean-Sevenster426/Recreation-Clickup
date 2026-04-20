import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.db import connection

# Check if migration is recorded
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT id, app, name, applied
        FROM django_migrations
        WHERE app='home'
        ORDER BY id DESC
        LIMIT 10
    """)
    migrations = cursor.fetchall()

    print("Recent migrations for 'home' app:")
    print("-" * 80)
    for migration in migrations:
        print(f"ID: {migration[0]}, App: {migration[1]}, Name: {migration[2]}, Applied: {migration[3]}")

    # Check if 0005_devmessage exists
    cursor.execute("""
        SELECT COUNT(*)
        FROM django_migrations
        WHERE app='home' AND name='0005_devmessage'
    """)
    count = cursor.fetchone()[0]
    print(f"\nMigration 0005_devmessage recorded: {count > 0}")

    # Check if table exists
    cursor.execute("""
        SHOW TABLES LIKE 'home_devmessage'
    """)
    table_exists = cursor.fetchone() is not None
    print(f"Table home_devmessage exists: {table_exists}")
