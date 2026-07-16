-- phpMyAdmin SQL Dump
-- Host: 127.0.0.1
-- Generation Time: Jul 16, 2026
-- Server version: 10.4.24-MariaDB (Typical XAMPP)
-- PHP Version: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `ivs`
--
CREATE DATABASE IF NOT EXISTS `ivs` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `ivs`;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `asset`
--

CREATE TABLE `asset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `price` float NOT NULL,
  `category` varchar(50) NOT NULL,
  `description` text NOT NULL,
  `status` varchar(20) DEFAULT 'Active',
  `image_filename` varchar(100) DEFAULT 'product-1.png',
  `created_at` datetime DEFAULT current_timestamp(),
  `seller_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `seller_id` (`seller_id`),
  CONSTRAINT `asset_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `transaction`
--

CREATE TABLE `transaction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `asset_id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `date_purchased` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `asset_id` (`asset_id`),
  KEY `buyer_id` (`buyer_id`),
  CONSTRAINT `transaction_ibfk_1` FOREIGN KEY (`asset_id`) REFERENCES `asset` (`id`) ON DELETE CASCADE,
  CONSTRAINT `transaction_ibfk_2` FOREIGN KEY (`buyer_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

COMMIT;
