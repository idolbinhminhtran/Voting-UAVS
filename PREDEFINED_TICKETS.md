# Pre-defined Ticket System

The voting system now uses a pre-defined ticket code system instead of admin-generated random codes. This provides better control and security for the voting process.

## How It Works

1. **Pre-defined Codes**: All valid ticket codes are defined in `app/predefined_tickets.py`
2. **Validation**: Only codes in the pre-defined list are considered valid
3. **Auto-creation**: When a valid pre-defined code is used for the first time, it's automatically added to the database
4. **No Admin Generation**: Admins can no longer generate random ticket codes

## Benefits

- **Security**: No random codes that could be guessed
- **Control**: Complete control over who gets valid tickets
- **Predictability**: All valid codes are known in advance
- **Simplicity**: No need for complex ticket generation systems

## Current Pre-defined Tickets

The system includes 15 pre-defined ticket codes based on seat numbers:

### D13 Section (6 seats)
- `D13.1`
- `D13.2`
- `D13.3`
- `D13.4`
- `D13.5`
- `D13.6`

### A2.R3 Section (8 seats)
- `A2.R3.1`
- `A2.R3.2`
- `A2.R3.3`
- `A2.R3.4`
- `A2.R3.5`
- `A2.R3.6`
- `A2.R3.7`
- `A2.R3.8`

### A1.R3 Section (1 seat)
- `A1.R3.2`

## Managing Pre-defined Tickets

### Adding New Tickets

1. Edit `app/predefined_tickets.py`
2. Add new codes to the `PREDEFINED_TICKETS` list
3. Restart the application
4. Run sync command to update database

### Syncing to Database

Use the admin panel or run the script:

```bash
python scripts/init_predefined_tickets.py --sync
```

### Viewing All Tickets

```bash
python scripts/init_predefined_tickets.py --list
```

## Admin Interface Changes

- **Old**: "Generate New Tickets" button
- **New**: "Sync Pre-defined Tickets" button

The sync function will:
- Add any new pre-defined codes to the database
- Leave existing tickets unchanged
- Show how many new tickets were synced

## API Changes

### New Endpoint
- `POST /api/admin/sync-predefined-tickets` - Sync pre-defined tickets to database

### Removed Endpoint
- `POST /api/admin/generate-tickets` - No longer available

## Database Behavior

1. **Ticket Validation**: 
   - First checks if code is in pre-defined list
   - If not in list, ticket is invalid regardless of database status
   
2. **Auto-creation**:
   - Valid pre-defined codes are auto-created in database when first used
   - Created as unused by default
   
3. **Usage Tracking**:
   - Once a ticket is used for voting, it's marked as used
   - Used tickets cannot vote again

## Security Considerations

- All valid codes are hardcoded in the application
- No possibility of guessing valid codes
- Complete audit trail of all possible tickets
- Easy to revoke tickets by removing from pre-defined list

## Deployment Notes

When deploying:
1. Ensure `app/predefined_tickets.py` contains all desired codes
2. Run the sync script or use admin panel to sync tickets
3. Distribute only the valid ticket codes to authorized users

## Example Usage

```python
from app.predefined_tickets import is_valid_ticket_code, get_predefined_tickets

# Check if a code is valid
if is_valid_ticket_code("DEMOUGT1"):
    print("Valid ticket code")

# Get all pre-defined codes
all_tickets = get_predefined_tickets()
print(f"Total pre-defined tickets: {len(all_tickets)}")
```
