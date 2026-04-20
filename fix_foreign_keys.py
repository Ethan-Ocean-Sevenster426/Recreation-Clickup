#!/usr/bin/env python
"""
Script to fix foreign key constraints that reference auth_user instead of main_user
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.db import connection

def fix_foreign_keys():
    """Fix foreign key constraints to point to main_user instead of auth_user"""

    print("="*60)
    print("Fixing Foreign Key Constraints")
    print("="*60)

    with connection.cursor() as cursor:
        # Get all foreign keys that reference auth_user
        print("\n[STEP 1] Finding foreign keys that reference auth_user...")
        cursor.execute("""
            SELECT
                TABLE_NAME,
                CONSTRAINT_NAME,
                COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_NAME = 'auth_user'
            AND TABLE_SCHEMA = DATABASE()
            ORDER BY TABLE_NAME
        """)

        fk_constraints = cursor.fetchall()

        if not fk_constraints:
            print("[INFO] No foreign keys found referencing auth_user")
            return

        print(f"[FOUND] {len(fk_constraints)} foreign keys to fix:")
        for table, constraint, column in fk_constraints:
            print(f"  - {table}.{column} ({constraint})")

        # Fix each foreign key
        print("\n[STEP 2] Updating foreign keys to reference main_user...")
        fixed_count = 0
        failed_count = 0

        for table, constraint, column in fk_constraints:
            try:
                print(f"\n[ACTION] Fixing {table}.{column}...")

                # Drop the old foreign key constraint
                print(f"  Dropping constraint {constraint}...")
                cursor.execute(f"ALTER TABLE `{table}` DROP FOREIGN KEY `{constraint}`")

                # Add new foreign key constraint pointing to main_user
                new_constraint = constraint.replace('auth_user', 'main_user')
                print(f"  Adding new constraint {new_constraint}...")
                cursor.execute(f"""
                    ALTER TABLE `{table}`
                    ADD CONSTRAINT `{new_constraint}`
                    FOREIGN KEY (`{column}`)
                    REFERENCES `main_user` (`id`)
                """)

                print(f"  [SUCCESS] Fixed {table}.{column}")
                fixed_count += 1

            except Exception as e:
                print(f"  [ERROR] Failed to fix {table}.{column}: {e}")
                failed_count += 1

        print("\n" + "="*60)
        print(f"Summary:")
        print(f"  Total foreign keys found: {len(fk_constraints)}")
        print(f"  Successfully fixed: {fixed_count}")
        print(f"  Failed: {failed_count}")
        print("="*60)

        if fixed_count > 0:
            print("\n[SUCCESS] Foreign keys have been updated!")
            print("The dashboard should now work properly.")
        else:
            print("\n[WARNING] No foreign keys were fixed.")

if __name__ == '__main__':
    try:
        fix_foreign_keys()
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
