-- Initialize sandbox database
CREATE DATABASE IF NOT EXISTS sandbox_db;
CREATE USER IF NOT EXISTS 'sandbox_user'@'%' IDENTIFIED BY 'sandbox_password';
GRANT ALL PRIVILEGES ON sandbox_db.* TO 'sandbox_user'@'%';
FLUSH PRIVILEGES;