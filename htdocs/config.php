<?php
// Database configuration file
// Store this file outside the web root for better security in production

define('DB_HOST', 'localhost');
define('DB_NAME', 'personal_chatbot');
define('DB_USER', 'root');
define('DB_PASS', '');

// Create connection using MySQLi with prepared statements
try {
    $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
    
    // Check connection
    if ($conn->connect_error) {
        throw new Exception("Connection failed: " . $conn->connect_error);
    }
    
    // Set charset to utf8mb4 for better Unicode support
    $conn->set_charset("utf8mb4");
    
} catch (Exception $e) {
    // Log error in production, show generic message to users
    error_log("Database connection error: " . $e->getMessage());
    die("Connection failed. Please try again later.");
}

// Start session if not already started
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

?>

<!-- 
Instructions for setup:
1. Import users.sql into your MySQL database using phpMyAdmin
2. Update the database credentials above if needed
3. Make sure this config.php file is included in all PHP files that need database access
4. For production, consider moving this file outside the web root directory
-->