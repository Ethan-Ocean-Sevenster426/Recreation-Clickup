import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.db import connection
from home.models import DevMessage

# Try to query the table
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM home_devmessage")
        count = cursor.fetchone()[0]
        print(f"[OK] Table exists! Current row count: {count}")

        # Get table structure
        cursor.execute("DESCRIBE home_devmessage")
        columns = cursor.fetchall()
        print("\nTable structure:")
        print("-" * 80)
        for col in columns:
            print(f"{col[0]}: {col[1]}")

except Exception as e:
    print(f"[ERROR] Error accessing table: {e}")

# Try using Django ORM
try:
    count = DevMessage.objects.count()
    print(f"\n[OK] Django ORM works! Message count: {count}")
except Exception as e:
    print(f"\n[ERROR] Django ORM error: {e}")
