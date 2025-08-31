#!/usr/bin/env python3
"""
Script to add the 10 finalists to the database
"""

import sqlite3
from datetime import datetime

def add_contestants():
    """Add the 10 finalists to the database"""
    conn = sqlite3.connect('voting.db')
    
    # Check if contestants already exist
    cursor = conn.execute('SELECT COUNT(*) FROM contestants')
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        print(f"Database already has {existing_count} contestants")
        print("Clearing existing contestants...")
        conn.execute('DELETE FROM contestants')
        conn.commit()
    
    print("Adding 10 finalists...")
    
    # The 10 finalists from the image
    contestants = [
        {
            'name': 'Anne and Quang',
            'description': 'Dynamic duo with exceptional talent',
            'image_url': '/images/default-avatar.svg'
        },
        {
            'name': 'HORIZON',
            'description': 'Innovative musical group pushing boundaries',
            'image_url': '/images/default-avatar.svg'
        },
        {
            'name': 'Truong Ho Quan Minh',
            'description': 'Solo artist with unique style',
            'image_url': '/images/default-avatar.svg'
        },
        {
            'name': 'BlackB',
            'description': 'Contemporary music collective',
            'image_url': '/images/default-avatar.svg'
        },
        {
            'name': 'Ban Nhac Anh Em',
            'description': 'Brotherhood band with harmonious sound',
            'image_url': '/images/default-avatar.svg'
        },
        {
            'name': 'Nguyen Tan Phuc',
            'description': 'Versatile performer with wide range',
            'image_url': '/images/default-avatar.svg'
        },
        {
            'name': 'Anne Vu',
            'description': 'Solo artist with powerful vocals',
            'image_url': '/images/default-avatar.svg'
        },
        {
            'name': 'Nguyen Ngoc Minh Anh',
            'description': 'Emerging talent with fresh perspective',
            'image_url': '/images/default-avatar.svg'
        },
        {
            'name': 'Son Truong Nguyen',
            'description': 'Experienced performer with stage presence',
            'image_url': '/images/default-avatar.svg'
        },
        {
            'name': 'Tran Nguyen Tony',
            'description': 'Dynamic performer with international appeal',
            'image_url': '/images/default-avatar.svg'
        }
    ]
    
    # Insert contestants
    for contestant in contestants:
        conn.execute(
            '''INSERT INTO contestants 
               (name, description, image_url, is_active, created_at) 
               VALUES (?, ?, ?, ?, ?)''',
            (
                contestant['name'],
                contestant['description'],
                contestant['image_url'],
                1,  # is_active
                datetime.utcnow()
            )
        )
    
    conn.commit()
    conn.close()
    
    print("✅ Added 10 finalists successfully!")
    print("\nFinalists:")
    for i, contestant in enumerate(contestants, 1):
        print(f"  {i:2d}. {contestant['name']}")

if __name__ == "__main__":
    add_contestants()
