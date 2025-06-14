#!/usr/bin/env python3
"""
Database Migration Runner
Applies database migrations to update existing installations
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import glob
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get database connection from environment variables"""
    database_url = os.getenv("DATABASE_URL", "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard")
    
    # Parse the database URL
    if database_url.startswith("postgresql://"):
        # Remove postgresql:// prefix
        url_parts = database_url[13:].split("@")
        user_pass = url_parts[0].split(":")
        host_db = url_parts[1].split("/")
        host_port = host_db[0].split(":")
        
        return {
            "host": host_port[0],
            "port": int(host_port[1]) if len(host_port) > 1 else 5432,
            "database": host_db[1],
            "user": user_pass[0],
            "password": user_pass[1]
        }
    else:
        raise ValueError("Invalid DATABASE_URL format")

def create_migrations_table(cursor):
    """Create migrations tracking table if it doesn't exist"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✅ Migrations tracking table ready")

def get_applied_migrations(cursor):
    """Get list of already applied migrations"""
    cursor.execute("SELECT migration_name FROM schema_migrations ORDER BY applied_at")
    return [row[0] for row in cursor.fetchall()]

def get_pending_migrations(migrations_dir):
    """Get list of migration files that need to be applied"""
    migration_files = glob.glob(os.path.join(migrations_dir, "*.sql"))
    migration_files.sort()  # Apply in order
    return [os.path.basename(f) for f in migration_files]

def apply_migration(cursor, migration_file, migrations_dir):
    """Apply a single migration file"""
    migration_path = os.path.join(migrations_dir, migration_file)
    
    print(f"📄 Applying migration: {migration_file}")
    
    try:
        with open(migration_path, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Execute the migration
        cursor.execute(migration_sql)
        
        # Record that this migration was applied
        cursor.execute(
            "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
            (migration_file,)
        )
        
        print(f"✅ Successfully applied: {migration_file}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply {migration_file}: {str(e)}")
        return False

def main():
    """Main migration runner"""
    print("🚀 Database Migration Runner")
    print("=" * 50)
    
    # Get migrations directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    migrations_dir = project_root / "docker" / "migrations"
    
    if not migrations_dir.exists():
        print(f"❌ Migrations directory not found: {migrations_dir}")
        sys.exit(1)
    
    print(f"📁 Migrations directory: {migrations_dir}")
    
    # Get database connection
    try:
        db_config = get_database_connection()
        print(f"🔗 Connecting to database: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
    except Exception as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        sys.exit(1)
    
    try:
        # Create migrations table
        create_migrations_table(cursor)
        
        # Get applied and pending migrations
        applied_migrations = get_applied_migrations(cursor)
        pending_migrations = get_pending_migrations(str(migrations_dir))
        
        print(f"📊 Applied migrations: {len(applied_migrations)}")
        print(f"📊 Available migrations: {len(pending_migrations)}")
        
        # Filter out already applied migrations
        migrations_to_apply = [m for m in pending_migrations if m not in applied_migrations]
        
        if not migrations_to_apply:
            print("✅ All migrations are up to date!")
            return
        
        print(f"📊 Migrations to apply: {len(migrations_to_apply)}")
        print()
        
        # Apply each pending migration
        success_count = 0
        for migration_file in migrations_to_apply:
            if apply_migration(cursor, migration_file, str(migrations_dir)):
                success_count += 1
            else:
                print(f"❌ Migration failed, stopping at: {migration_file}")
                break
        
        print()
        print("=" * 50)
        print(f"✅ Successfully applied {success_count} migrations")
        
        if success_count == len(migrations_to_apply):
            print("🎉 All migrations completed successfully!")
        else:
            print("⚠️  Some migrations failed. Please check the errors above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration process failed: {str(e)}")
        sys.exit(1)
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
