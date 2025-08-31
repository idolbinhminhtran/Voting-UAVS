"""
Database adapter for supporting both SQLite and PostgreSQL/Supabase
"""
import os
import sqlite3
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from .config import Config
import logging

logger = logging.getLogger(__name__)

class DatabaseAdapter:
    """Database adapter that works with both SQLite and PostgreSQL"""
    
    def __init__(self):
        self.db_type = Config.DATABASE_TYPE
        self.db_url = Config.DATABASE_URL
        
    @contextmanager
    def get_connection(self):
        """Get database connection based on database type"""
        if self.db_type == 'postgresql':
            conn = psycopg2.connect(self.db_url)
            conn.set_session(autocommit=False)
            try:
                yield conn
            finally:
                conn.close()
        else:  # SQLite
            db_path = self.db_url.replace('sqlite:///', '')
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a query and return results"""
        with self.get_connection() as conn:
            if self.db_type == 'postgresql':
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            else:
                cursor = conn.cursor()
            
            try:
                cursor.execute(query, params or ())
                
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount
                
                conn.commit()
                return result
            except Exception as e:
                conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_function(self, func_name, params=None):
        """Execute a PostgreSQL function (for Supabase)"""
        if self.db_type != 'postgresql':
            raise NotImplementedError("Functions are only supported in PostgreSQL")
        
        param_placeholders = ', '.join(['%s'] * len(params)) if params else ''
        query = f"SELECT * FROM {func_name}({param_placeholders})"
        
        return self.execute_query(query, params, fetch_all=True)
    
    def get_table_schema(self, table_name):
        """Get table schema for validation"""
        if self.db_type == 'postgresql':
            query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """
        else:
            query = f"PRAGMA table_info({table_name})"
        
        return self.execute_query(query, (table_name,) if self.db_type == 'postgresql' else None, fetch_all=True)

# Global database adapter instance
db_adapter = DatabaseAdapter()

def get_db_connection():
    """Legacy function for backward compatibility"""
    return db_adapter.get_connection()

def migrate_to_postgresql():
    """Helper function to migrate from SQLite to PostgreSQL"""
    if Config.DATABASE_TYPE == 'sqlite':
        logger.info("Database is already SQLite, no migration needed")
        return
    
    # This would be used to migrate existing SQLite data to PostgreSQL
    # Implementation depends on specific migration requirements
    logger.info("PostgreSQL migration not implemented yet")
