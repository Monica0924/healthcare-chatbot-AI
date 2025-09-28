<?php
/**
 * Logout script for Personal Chatbot Application
 * 
 * This script handles user logout by:
 * 1. Starting/initializing the session
 * 2. Clearing all session variables
 * 3. Destroying the session completely
 * 4. Redirecting to the login page
 */

// Initialize the session if not already started
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Unset all of the session variables to clear user data
$_SESSION = array();

// Destroy the session completely
session_destroy();

// Redirect to login page
header("Location: login.php");
exit();
?>