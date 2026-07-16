-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 16, 2026 at 02:30 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ivs`
--

-- --------------------------------------------------------

--
-- Table structure for table `address`
--

CREATE TABLE `address` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `recipient_name` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `street_address` text NOT NULL,
  `is_default` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `address`
--

INSERT INTO `address` (`id`, `user_id`, `recipient_name`, `phone`, `street_address`, `is_default`) VALUES
(1, 4, 'Jeric', 'h', 'bagumabyaa', 1),
(2, 4, 'jhah', '1276', 'paete', 0);

-- --------------------------------------------------------

--
-- Table structure for table `asset`
--

CREATE TABLE `asset` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `price` float NOT NULL,
  `category` varchar(50) NOT NULL,
  `description` text NOT NULL,
  `status` varchar(20) DEFAULT 'Active',
  `image_filename` varchar(100) DEFAULT 'product-1.png',
  `created_at` datetime DEFAULT current_timestamp(),
  `seller_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `asset`
--

INSERT INTO `asset` (`id`, `name`, `price`, `category`, `description`, `status`, `image_filename`, `created_at`, `seller_id`) VALUES
(1, 'Paete Farm', 20000, 'Jewelry', 'h', 'Sold', 'Gemini_Generated_Image_n71ggn71ggn71ggn (1).png', '2026-07-16 11:09:47', 2);

-- --------------------------------------------------------

--
-- Table structure for table `transaction`
--

CREATE TABLE `transaction` (
  `id` int(11) NOT NULL,
  `asset_id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `date_purchased` datetime DEFAULT current_timestamp(),
  `address_id` int(11) DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transaction`
--

INSERT INTO `transaction` (`id`, `asset_id`, `buyer_id`, `date_purchased`, `address_id`, `payment_method`) VALUES
(1, 1, 4, '2026-07-16 11:50:35', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `first_name`, `last_name`, `email`, `password_hash`, `role`, `phone`, `address`) VALUES
(1, 'Jeric', 'Punay', 'punay.jeric@gmail.com', 'pbkdf2:sha256:600000$xQgzxR5lfecsPjZR$654429fc9a766082b08f316bae1acc827d094c77c0f02f72448d8ea0a17ec00e', 'seller', NULL, NULL),
(2, 'Admin', 'Seller', 'seller@ivs.com', 'pbkdf2:sha256:600000$zOf08c305HzA2Noc$79d6c7834b771078206c2d9f08b3a4c72e2c00abf6a9bd3ad1ac33a89998c9ea', 'seller', NULL, NULL),
(3, 'Urahara ', 'Kisuke', 'uarhara.kisuke@gmail.com', 'pbkdf2:sha256:600000$bmBfxBVfoGUx4PzB$079a6546f0c0772cfa5eb3517f92f935a834d4fb3adc639e55c03522bfa7777c', 'buyer', NULL, NULL),
(4, 'Jasmine', 'Araza', 'jasmine.araza@gmail.com', 'pbkdf2:sha256:600000$LJD77kEbhzFb37TC$21124182c9544aa52cd86a7d51ac726db814fa6a6e1a517653a6a60e195e8e56', 'buyer', NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `address`
--
ALTER TABLE `address`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `asset`
--
ALTER TABLE `asset`
  ADD PRIMARY KEY (`id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `transaction`
--
ALTER TABLE `transaction`
  ADD PRIMARY KEY (`id`),
  ADD KEY `asset_id` (`asset_id`),
  ADD KEY `buyer_id` (`buyer_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `address`
--
ALTER TABLE `address`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `asset`
--
ALTER TABLE `asset`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `transaction`
--
ALTER TABLE `transaction`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `address`
--
ALTER TABLE `address`
  ADD CONSTRAINT `address_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Constraints for table `asset`
--
ALTER TABLE `asset`
  ADD CONSTRAINT `asset_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `transaction`
--
ALTER TABLE `transaction`
  ADD CONSTRAINT `transaction_ibfk_1` FOREIGN KEY (`asset_id`) REFERENCES `asset` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `transaction_ibfk_2` FOREIGN KEY (`buyer_id`) REFERENCES `user` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
