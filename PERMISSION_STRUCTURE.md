# E-Click Permission Structure

## User Levels

### 1. Client (Regular User)
- **is_staff**: False
- **is_superuser**: False

**Access:**
- Dashboard
- My Projects (only assigned projects)
- Send Message
- Settings
- Logout

**No Access To:**
- Team Dashboard
- Admin Control
- Reports
- Analytics
- Send Report
- Satisfaction Report
- System Logs
- Backup Management

---

### 2. Team Member (Staff)
- **is_staff**: True
- **is_superuser**: False

**Access:**
- Dashboard
- All Projects (full project list)
- Team Dashboard
- Send Message
- Settings
- Logout

**No Access To:**
- Admin Control
- Reports
- Analytics
- Send Report
- Satisfaction Report
- System Logs
- Backup Management

---

### 3. Admin (Superuser)
- **is_staff**: True
- **is_superuser**: True

**Full Access To Everything:**
- Dashboard
- All Projects
- Team Dashboard
- Admin Control
- Reports
- Analytics
- Send Report
- Satisfaction Report
- Send Message
- System Logs
- Backup Management
- Settings
- Logout

---

## Current Users

### Ethan
- **Username**: ethan
- **Email**: ethansevenster5@gmail.com
- **Password**: Ethan123!
- **Level**: Team Member (Staff)
- **is_staff**: True
- **is_superuser**: False

---

## Implementation Details

### Navigation (dashboard_base.html)
- Admin-only items wrapped in `{% if user.is_superuser %}`
- Team member items wrapped in `{% if user.is_staff %}`
- Client items have no restrictions (except Team Dashboard)

### Views (home/views.py)
All admin-only views check for superuser status:
```python
if not request.user.is_superuser:
    messages.error(request, 'Access denied. Admin privileges required.')
    return redirect('dashboard')
```

**Admin-Only Views:**
- `analytics()` - Line 389
- `reports()` - Line 1107
- `admin_control()` - Line 4351
- `send_report()` - Line 5633
- `system_logs()` - Line 7830
- `satisfaction_report()` - Line 9256
- `backup_management()` - Line 8519 (already had is_superuser check)

**Team Member Views:**
- `team_dashboard()` - Line 6894 (checks is_staff)

---

## Testing

To test the permission structure:

1. **As Client**: Log in with a client account (is_staff=False)
   - Should only see: Dashboard, My Projects, Send Message, Settings

2. **As Team Member**: Log in as ethan (is_staff=True, is_superuser=False)
   - Should see: Dashboard, All Projects, Team Dashboard, Send Message, Settings
   - Should NOT see: Admin Control, Reports, Analytics, Send Report, Satisfaction Report, System Logs, Backup Management

3. **As Admin**: Log in with admin account (is_superuser=True)
   - Should see all navigation items and have access to all pages
