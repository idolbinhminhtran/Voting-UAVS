#!/usr/bin/env python3
"""
Script to generate 400 unique ticket codes and export to CSV
Usage: python generate_tickets.py [output_file.csv]
"""

import csv
import sys
import os
import random
import string
from datetime import datetime

def generate_ticket_code(length=8):
    """Generate a random ticket code"""
    # Use uppercase letters and numbers, avoid confusing characters
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    
    code = ''.join(random.choice(chars) for _ in range(length))
    return code

def generate_unique_tickets(count=400, length=8):
    """Generate unique ticket codes"""
    tickets = set()
    
    while len(tickets) < count:
        code = generate_ticket_code(length)
        tickets.add(code)
    
    return list(tickets)

def export_to_csv(tickets, filename):
    """Export tickets to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Ticket Code', 'Generated At', 'Status'])
        
        # Write ticket data
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for ticket in tickets:
            writer.writerow([ticket, current_time, 'Unused'])

def main():
    # Determine output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'tickets_{timestamp}.csv'
    
    print(f"Generating 400 unique ticket codes...")
    
    # Generate tickets
    tickets = generate_unique_tickets(400, 8)
    
    # Export to CSV
    export_to_csv(tickets, output_file)
    
    print(f"Successfully generated {len(tickets)} tickets")
    print(f"Exported to: {output_file}")
    
    # Show sample tickets
    print("\nSample tickets:")
    for i, ticket in enumerate(tickets[:10]):
        print(f"  {i+1:2d}. {ticket}")
    
    if len(tickets) > 10:
        print(f"  ... and {len(tickets) - 10} more")
    
    # Verify uniqueness
    unique_count = len(set(tickets))
    if unique_count == len(tickets):
        print(f"\n✓ All {unique_count} tickets are unique")
    else:
        print(f"\n⚠ Warning: Only {unique_count} unique tickets out of {len(tickets)}")

if __name__ == "__main__":
    main()
