# E-Click Backup System

This document explains how to use the comprehensive backup and restore system for your E-Click Django application.

## Overview

The backup system provides multiple ways to protect your data:
- **Manual Backups**: Create backups through the web interface
- **Upload Backups**: Upload existing backup files from other systems
- **Automatic Backups**: Scheduled backups using management commands
- **Restore Functionality**: Restore your database to any previous backup point
- **Data Integrity**: All backups include checksums for verification

## Features

### 1. Web Interface
- Access via `/backup-management/` URL (admin only)
- Create new backups with descriptions
- Upload existing backup files
- View all backups with metadata
- Download, restore, or delete backups
- Backup statistics and overview

### 2. Management Commands
- `python manage.py create_automatic_backup` - Create automatic backup
- `python manage.py restore_backup <backup_id>` - Restore from backup

### 3. Safety Features
- Automatic safety backup before restore operations
- File integrity verification using SHA256 checksums
- Backup metadata tracking (size, type, creation date, etc.)

## Usage

### Creating a Manual Backup

1. Navigate to **Backup Management** in the admin panel
2. Fill in an optional description
3. Click **Create Backup**
4. The system will create a JSON backup file with all your data

### Uploading an Existing Backup

1. Go to the **Upload Backup File** section
2. Select a JSON backup file
3. Add an optional description
4. Click **Upload Backup**
5. The file will be validated and stored

### Restoring from a Backup

1. In the **Existing Backups** section, find the backup you want to restore
2. Click the **Restore** button (warning icon)
3. Confirm the restore operation
4. A safety backup of your current data will be created automatically
5. The database will be restored from the selected backup

### Downloading a Backup

1. Find the backup in the **Existing Backups** section
2. Click the **Download** button
3. The backup file will be downloaded to your computer

## Management Commands

### Create Automatic Backup

```bash
# Basic automatic backup
python manage.py create_automatic_backup

# With description
python manage.py create_automatic_backup --description "Daily backup"

# With cleanup of old backups (keep last 30 days)
python manage.py create_automatic_backup --cleanup --keep-days 30

# With custom retention period
python manage.py create_automatic_backup --cleanup --keep-days 7
```

### Restore from Backup

```bash
# Interactive restore (with confirmation)
python manage.py restore_backup 1

# Force restore without confirmation
python manage.py restore_backup 1 --force

# Skip safety backup (not recommended)
python manage.py restore_backup 1 --no-safety-backup
```

## Scheduling Automatic Backups

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 2:00 AM)
4. Action: Start a program
5. Program: `python`
6. Arguments: `manage.py create_automatic_backup --cleanup --keep-days 30`
7. Start in: Your project directory

### Linux/Mac Cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2:00 AM
0 2 * * * cd /path/to/your/project && python manage.py create_automatic_backup --cleanup --keep-days 30
```

## Backup File Format

Backups are created using Django's `dumpdata` command and stored as JSON files:
- **Location**: `backups/` directory in your project
- **Format**: JSON with all model data
- **Exclusions**: System tables (contenttypes, auth.permission, admin.logentry, sessions.session)
- **Naming**: `backup_YYYYMMDD_HHMMSS.json` or `auto_backup_YYYYMMDD_HHMMSS.json`

## Backup Types

1. **Manual Backup**: Created by administrators through the web interface
2. **Automatic Backup**: Created by scheduled management commands
3. **Uploaded Backup**: Files uploaded from external sources
4. **Safety Backup**: Automatically created before restore operations

## Backup Status

- **Available**: Backup file exists and is ready for use
- **Corrupted**: File integrity check failed
- **Restored**: Backup has been used to restore the database

## Security Considerations

- Only superusers can access backup management
- All backup operations are logged in the system logs
- Backup files are stored in the `backups/` directory
- Consider encrypting backup files for sensitive data
- Regularly test restore procedures

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure you're logged in as a superuser
2. **Backup Creation Failed**: Check disk space and file permissions
3. **Restore Failed**: Verify backup file integrity and database connectivity
4. **Import Errors**: Ensure backup file format is correct (JSON)

### File Locations

- **Backup Files**: `backups/` directory
- **Database**: `db.sqlite3` (or your configured database)
- **Logs**: Check system logs for backup operation details

### Performance Notes

- Large databases may take time to backup/restore
- Consider running backups during low-traffic periods
- Monitor disk space usage in the backups directory
- Regular cleanup of old backups helps maintain performance

## Best Practices

1. **Regular Backups**: Create backups daily or weekly depending on data change frequency
2. **Multiple Locations**: Store backups in different physical locations
3. **Test Restores**: Periodically test restore procedures
4. **Monitor Space**: Keep track of backup directory size
5. **Document Procedures**: Maintain clear documentation of backup/restore processes
6. **Version Control**: Keep track of backup versions and their contents

## Support

If you encounter issues with the backup system:
1. Check the system logs for error details
2. Verify file permissions and disk space
3. Ensure all required models are properly imported
4. Check Django version compatibility

## File Structure

```
backups/
├── backup_20250812_143022.json
├── auto_backup_20250812_020000.json
├── uploaded_backup_20250812_100000.json
└── pre_restore_safety_20250812_150000.json
```

The backup system is designed to be robust and user-friendly while providing comprehensive data protection for your E-Click application.
