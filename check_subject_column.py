import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("DESCRIBE home_devmessage")
    for row in cursor.fetchall():
        if 'subject' in row[0].lower():
            print(f"{row[0]}: {row[1]}")
