-- Initialize sandbox database
CREATE DATABASE IF NOT EXISTS sandbox_platform;
CREATE USER IF NOT EXISTS 'sandbox_user'@'%' IDENTIFIED BY 'sandbox_password';
GRANT ALL PRIVILEGES ON sandbox_platform.* TO 'sandbox_user'@'%';
FLUSH PRIVILEGES;