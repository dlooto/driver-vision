-- MySQL dump 10.13  Distrib 5.5.41, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: vision
-- ------------------------------------------------------
-- Server version	5.5.41-0ubuntu0.12.04.1-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `vision_road`
--

DROP TABLE IF EXISTS `vision_road`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vision_road` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_time` datetime NOT NULL,
  `name` varchar(40) DEFAULT NULL,
  `is_real` tinyint(1) NOT NULL,
  `is_valid` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vision_road`
--

LOCK TABLES `vision_road` WRITE;
/*!40000 ALTER TABLE `vision_road` DISABLE KEYS */;
INSERT INTO `vision_road` VALUES (1,'2015-10-30 16:08:31','熊猫路',1,1),(2,'2015-10-30 17:03:07','觉梦路',1,1),(3,'2015-10-30 17:03:20','锁庆路',1,1),(4,'2015-10-30 17:03:31','宁远路',1,1),(5,'2015-10-30 17:03:42','专离路',1,1),(6,'2015-10-30 17:03:51','罗马路',1,1),(7,'2015-10-30 17:03:59','独忆路',1,1),(8,'2015-10-30 17:04:07','转适路',1,1),(9,'2015-10-30 17:04:14','拥艺路',1,1),(10,'2015-10-30 17:04:21','习识路',1,1),(11,'2015-10-30 17:04:30','优暗路',1,1),(12,'2015-10-30 17:04:37','办卜路',1,1),(13,'2015-10-30 17:04:52','覺夢路',0,1),(14,'2015-10-30 17:04:57','鎖慶路',0,1),(15,'2015-10-30 17:05:04','寧遠路',0,1),(16,'2015-10-30 17:05:09','專離路',0,1),(17,'2015-10-30 17:05:15','羅馬路',0,1),(18,'2015-10-30 17:05:32','獨憶路',0,1),(19,'2015-10-30 17:05:41','轉適路',0,1),(20,'2015-10-30 17:05:50','擁藝路',0,1),(21,'2015-10-30 17:05:59','習識路',0,1),(22,'2015-10-30 17:06:06','優暗路',0,1),(23,'2015-10-30 17:06:33','辦藝路',0,1);
/*!40000 ALTER TABLE `vision_road` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-10-31 16:36:44
