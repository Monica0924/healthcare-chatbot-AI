# Personal Chatbot - PHP Authentication System

A secure PHP authentication system with MySQL database integration for a personal chatbot application.

## Features

- **Secure User Registration**: Form validation, email uniqueness check, password hashing
- **Secure Login**: Session management, password verification, error handling
- **Dashboard**: Welcome page for authenticated users
- **Logout**: Secure session destruction
- **Security Features**: 
  - Prepared statements to prevent SQL injection
  - Password hashing using `password_hash()` and `password_verify()`
  - Input validation and sanitization
  - Session security

## Files Created

1. **users.sql** - Database schema for users table
2. **config.php** - Database connection configuration
3. **signup.php** - User registration form and processing
4. **login.php** - User login form and authentication
5. **dashboard.php** - Welcome page for logged-in users
6. **logout.php** - Session destruction script

## Setup Instructions

### 1. Database Setup

1. Open phpMyAdmin in your web browser
2. Click on the "Import" tab
3. Click "Choose File" and select `users.sql`
4. Click "Go" to import the database schema

Alternatively, you can run the SQL commands manually:
```sql
CREATE DATABASE IF NOT EXISTS personal_chatbot;
USE personal_chatbot;
-- Then run the CREATE TABLE statement from users.sql
```

### 2. Configuration

1. Open `config.php`
2. Update the database credentials if needed:
   - `DB_HOST` - Usually 'localhost'
   - `DB_NAME` - Database name (default: 'personal_chatbot')
   - `DB_USER` - Database username (default: 'root')
   - `DB_PASS` - Database password (default: '')

### 3. File Placement

Place all files in your web server's document root (e.g., `htdocs` for XAMPP, `www` for WAMP).

### 4. Testing

1. Navigate to `http://localhost/signup.php`
2. Create a new account
3. Login with your credentials at `http://localhost/login.php`
4. You'll be redirected to the dashboard
5. Test logout functionality

## Security Features

### Password Security
- Passwords are hashed using PHP's `password_hash()` function with bcrypt algorithm
- Minimum password length of 6 characters
- Password confirmation to prevent typos

### SQL Injection Prevention
- All database queries use prepared statements
- Input validation and sanitization
- Parameter binding for all user inputs

### Session Security
- Session variables are properly initialized
- Session destruction on logout
- Session hijacking prevention

### Input Validation
- Email format validation
- Name validation (letters and spaces only)
- Duplicate email checking
- Form field sanitization

## Error Handling

- User-friendly error messages
- Generic error messages for security (e.g., "Invalid email or password")
- Proper error logging for debugging

## Customization

### Styling
The system uses Bootstrap 5 for styling. You can:
- Modify the CSS in each file's `<style>` section
- Add custom CSS files
- Change Bootstrap themes

### Database Fields
You can extend the users table by:
- Adding new columns to the SQL schema
- Updating the signup form
- Modifying the login logic

### Additional Features
Consider adding:
- Password reset functionality
- Email verification
- User profile management
- Remember me functionality

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL service is running
   - Verify database credentials in config.php
   - Ensure database exists

2. **Session Issues**
   - Check PHP session configuration
   - Ensure session_start() is called before any output

3. **Form Submission Errors**
   - Check PHP error logs
   - Verify all required fields are filled
   - Check for JavaScript conflicts

### Security Notes

- Always use HTTPS in production
- Consider rate limiting for login attempts
- Implement CSRF protection for forms
- Keep PHP and MySQL updated
- Use strong database passwords
- Consider implementing two-factor authentication

## Support

This is a basic authentication system. For production use, consider additional security measures and regular security audits.