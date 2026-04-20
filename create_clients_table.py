"""
Create the missing home_project_clients junction table for the ManyToMany relationship.
This script manually creates the table that should have been created by the migration.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eclick.settings')
django.setup()

from django.db import connection

def create_project_clients_table():
    """Create the home_project_clients junction table"""
    with connection.cursor() as cursor:
        # Drop table if it exists (in case of partial creation)
        cursor.execute("DROP TABLE IF EXISTS `home_project_clients`;")
        print("[OK] Dropped existing table if any")

        # Create the junction table
        create_table_sql = """
        CREATE TABLE `home_project_clients` (
            `id` bigint NOT NULL AUTO_INCREMENT,
            `project_id` bigint NOT NULL,
            `client_id` bigint NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `home_project_clients_project_id_client_id_uniq` (`project_id`, `client_id`),
            KEY `home_project_clients_project_id_idx` (`project_id`),
            KEY `home_project_clients_client_id_idx` (`client_id`),
            CONSTRAINT `home_project_clients_project_id_fk`
                FOREIGN KEY (`project_id`) REFERENCES `home_project` (`id`) ON DELETE CASCADE,
            CONSTRAINT `home_project_clients_client_id_fk`
                FOREIGN KEY (`client_id`) REFERENCES `home_client` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        cursor.execute(create_table_sql)
        print("[OK] Created home_project_clients table")
        print("[OK] Table structure:")
        print("     - id (bigint, PRIMARY KEY, AUTO_INCREMENT)")
        print("     - project_id (bigint, FOREIGN KEY -> home_project.id)")
        print("     - client_id (bigint, FOREIGN KEY -> home_client.id)")
        print("     - UNIQUE constraint on (project_id, client_id)")

if __name__ == "__main__":
    print("=" * 60)
    print("Creating home_project_clients ManyToMany Table")
    print("=" * 60)

    try:
        create_project_clients_table()
        print("\n" + "=" * 60)
        print("[SUCCESS] Table created successfully!")
        print("=" * 60)
        print("\nYou can now assign multiple clients to projects.")
    except Exception as e:
        print(f"\n[ERROR] Failed to create table: {str(e)}")
        print("\nPlease check your database connection and try again.")
