-- Database and table schema for login.php and signup.php
-- Creates a database named `chatbot` and a `users` table compatible with the code

-- Create database (change name if needed)
CREATE DATABASE IF NOT EXISTS `chatbot` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `chatbot`;

-- Users table
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(191) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Optional: sample user (email: demo@example.com, password: password)
-- The hash below is a bcrypt hash for the string "password"
INSERT INTO `users` (`name`, `email`, `password`) VALUES
('Demo User', 'demo@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi');


