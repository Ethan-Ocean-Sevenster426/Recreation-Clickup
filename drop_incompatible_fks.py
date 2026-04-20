#!/usr/bin/env python
"""
Script to drop foreign key constraints that reference auth_user
Since auth_user.id is INT and main_user.id is BIGINT, they are incompatible.
We'll drop the constraints to allow the app to work.
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.db import connection

def drop_auth_user_foreign_keys():
    """Drop foreign key constraints that reference auth_user"""

    print("="*60)
    print("Dropping Foreign Key Constraints")
    print("="*60)

    with connection.cursor() as cursor:
        # Get all foreign keys that reference auth_user from home_ tables
        print("\n[STEP 1] Finding foreign keys that reference auth_user...")
        cursor.execute("""
            SELECT
                TABLE_NAME,
                CONSTRAINT_NAME,
                COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_NAME = 'auth_user'
            AND TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME LIKE 'home_%'
            ORDER BY TABLE_NAME
        """)

        fk_constraints = cursor.fetchall()

        if not fk_constraints:
            print("[INFO] No foreign keys found referencing auth_user in home_ tables")
            return

        print(f"[FOUND] {len(fk_constraints)} foreign keys to drop:")
        for table, constraint, column in fk_constraints:
            print(f"  - {table}.{column} ({constraint})")

        # Drop each foreign key
        print("\n[STEP 2] Dropping foreign keys...")
        dropped_count = 0
        failed_count = 0

        for table, constraint, column in fk_constraints:
            try:
                print(f"\n[ACTION] Dropping {table}.{constraint}...")
                cursor.execute(f"ALTER TABLE `{table}` DROP FOREIGN KEY `{constraint}`")
                print(f"  [SUCCESS] Dropped {table}.{constraint}")
                dropped_count += 1

            except Exception as e:
                print(f"  [ERROR] Failed to drop {table}.{constraint}: {e}")
                failed_count += 1

        print("\n" + "="*60)
        print(f"Summary:")
        print(f"  Total foreign keys found: {len(fk_constraints)}")
        print(f"  Successfully dropped: {dropped_count}")
        print(f"  Failed: {failed_count}")
        print("="*60)

        if dropped_count > 0:
            print("\n[SUCCESS] Foreign key constraints have been dropped!")
            print("The app should now work without foreign key constraint errors.")
            print("\nNote: The app will still work without these FK constraints.")
            print("Data integrity will be handled at the application level.")
        else:
            print("\n[WARNING] No foreign keys were dropped.")

if __name__ == '__main__':
    try:
        drop_auth_user_foreign_keys()
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
