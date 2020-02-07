CREATE DATABASE sutdwth;

-- Default MySQL configurations
UPDATE mysql.user SET authentication_string=PASSWORD('password') WHERE User='root';  -- Set root password
DELETE FROM mysql.user WHERE User='';  -- Remove anonymous users
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');  -- Root can only connect locally
DROP DATABASE IF EXISTS test;  -- Drop test db
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';

-- Create user for remote connection
GRANT ALL PRIVILEGES ON sutdwth.* TO 'remote'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;

-- Enable support for UTF-8 characters (primarily for hackathon group names)
ALTER DATABASE sutdwth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tables will be automatically created by SQLAlchemy from the bot's code
USE sutdwth;