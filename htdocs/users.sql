-- Database: personal_chatbot
CREATE DATABASE IF NOT EXISTS personal_chatbot;
USE personal_chatbot;

-- Table structure for table `users` with patient profile fields
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `age` int(11) DEFAULT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `medical_history` text DEFAULT NULL,
  `allergies` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample data (optional - password is 'password123')
-- INSERT INTO `users` (`name`, `email`, `password`, `age`, `gender`, `phone`, `address`, `medical_history`, `allergies`) VALUES
-- ('Test User', 'test@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 25, 'Male', '1234567890', '123 Main St, City, State', 'No significant medical history', 'No known allergies');

-- SQL Schema for updated users table with patient profile fields
-- This schema includes all the required patient data fields:
-- - name (existing): Patient's full name
-- - email (existing): Patient's email address (unique)
-- - password (existing): Hashed password
-- - age (new): Patient's age in years
-- - gender (new): Patient's gender (Male, Female, Other)
-- - phone (new): Patient's contact phone number
-- - address (new): Patient's residential address
-- - medical_history (new): Patient's medical history details
-- - allergies (new): Patient's known allergies
-- - created_at (existing): Timestamp when account was created