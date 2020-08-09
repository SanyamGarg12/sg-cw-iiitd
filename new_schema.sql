-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema cw_portal
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema cw_portal
-- -----------------------------------------------------
DROP DATABASE IF EXISTS `cw_portal`;
CREATE SCHEMA IF NOT EXISTS `cw_portal` DEFAULT CHARACTER SET latin1 ;
USE `cw_portal` ;

-- -----------------------------------------------------
-- Table `cw_portal`.`studentportal_bug`
-- -----------------------------------------------------

CREATE TABLE `studentportal_customuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `batch_number` int,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `cw_portal`.`studentportal_bug` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NULL DEFAULT NULL,
  `suggestions` LONGTEXT NOT NULL,
  `rating` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `studentportal_bug_6340c63c` (`user_id` ASC) VISIBLE,
  CONSTRAINT `user_id_refs_id_7dfbec6d`
    FOREIGN KEY (`user_id`)
    REFERENCES `cw_portal`.`studentportal_customuser` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 19
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`studentportal_category`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`studentportal_category` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(300) NOT NULL,
  `description` VARCHAR(1000) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`studentportal_ngo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`studentportal_ngo` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(1000) NOT NULL,
  `link` VARCHAR(200) NOT NULL,
  `details` LONGTEXT NOT NULL,
  `category_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `studentportal_ngo_6f33f001` (`category_id` ASC) VISIBLE,
  CONSTRAINT `category_id_refs_id_b20acc3a`
    FOREIGN KEY (`category_id`)
    REFERENCES `cw_portal`.`studentportal_category` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 198
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`studentportal_project`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`studentportal_project` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `student_id` INT(11) NOT NULL,
  `title` VARCHAR(1000) NOT NULL,
  `date_created` DATETIME NOT NULL,
  `credits` INT(11) NOT NULL,
  `NGO_id` INT(11) NULL DEFAULT NULL,
  `NGO_name` VARCHAR(1000) NOT NULL,
  `NGO_details` VARCHAR(1000) NOT NULL,
  `NGO_super` VARCHAR(1000) NOT NULL,
  `NGO_super_contact` VARCHAR(100) NOT NULL,
  `goals` LONGTEXT NOT NULL,
  `schedule_text` LONGTEXT NOT NULL,
  `finish_date` DATETIME NULL DEFAULT NULL,
  `stage` INT(11) NOT NULL,
  `category_id` INT(11) NOT NULL,
  `deleted` TINYINT(1) NOT NULL,
  `presented` TINYINT(1) NOT NULL,
  `semester` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `studentportal_project_94741166` (`student_id` ASC) VISIBLE,
  INDEX `studentportal_project_0f7bcd35` (`NGO_id` ASC) VISIBLE,
  INDEX `studentportal_project_6f33f001` (`category_id` ASC) VISIBLE,
  CONSTRAINT `category_id_refs_id_7c5a8dbe`
    FOREIGN KEY (`category_id`)
    REFERENCES `cw_portal`.`studentportal_category` (`id`),
  CONSTRAINT `NGO_id_refs_id_75e65aed`
    FOREIGN KEY (`NGO_id`)
    REFERENCES `cw_portal`.`studentportal_ngo` (`id`),
  CONSTRAINT `student_id_refs_id_f6ab59ff`
    FOREIGN KEY (`student_id`)
    REFERENCES `cw_portal`.`studentportal_customuser` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 1560
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`studentportal_document`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`studentportal_document` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `document` VARCHAR(100) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `date_added` DATETIME NOT NULL,
  `category` INT(11) NOT NULL,
  `project_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `studentportal_document_37952554` (`project_id` ASC) VISIBLE,
  CONSTRAINT `project_id_refs_id_f1684a4a`
    FOREIGN KEY (`project_id`)
    REFERENCES `cw_portal`.`studentportal_project` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 3898
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`studentportal_edit`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`studentportal_edit` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `diff_text` LONGTEXT NOT NULL,
  `when` DATETIME NOT NULL,
  `project_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `studentportal_edit_b098ad43` (`project_id` ASC) VISIBLE,
  CONSTRAINT `studentp_project_id_5ff0736f0cae4632_fk_studentportal_project_id`
    FOREIGN KEY (`project_id`)
    REFERENCES `cw_portal`.`studentportal_project` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 652
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`studentportal_feedback`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`studentportal_feedback` (
  `project_id` INT(11) NOT NULL,
  `hours` INT(11) NOT NULL,
  `achievements` LONGTEXT NOT NULL,
  `experience` INT(11) NOT NULL,
  PRIMARY KEY (`project_id`),
  CONSTRAINT `project_id_refs_id_f5852028`
    FOREIGN KEY (`project_id`)
    REFERENCES `cw_portal`.`studentportal_project` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`supervisor_example`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`supervisor_example` (
  `project_id` INT(11) NOT NULL,
  `date_created` DATETIME NOT NULL,
  `likes_count` INT(11) NOT NULL,
  `comments_count` INT(11) NOT NULL,
  PRIMARY KEY (`project_id`),
  CONSTRAINT `project_id_refs_id_221ebb26`
    FOREIGN KEY (`project_id`)
    REFERENCES `cw_portal`.`studentportal_project` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`supervisor_comment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`supervisor_comment` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `text` VARCHAR(200) NOT NULL,
  `project_id` INT(11) NOT NULL,
  `commentor_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `supervisor_comment_37952554` (`project_id` ASC) VISIBLE,
  INDEX `supervisor_comment_eb03c25c` (`commentor_id` ASC) VISIBLE,
  CONSTRAINT `commentor_id_refs_id_99b9dc4e`
    FOREIGN KEY (`commentor_id`)
    REFERENCES `cw_portal`.`studentportal_customuser` (`id`),
  CONSTRAINT `project_id_refs_project_id_75bd14ab`
    FOREIGN KEY (`project_id`)
    REFERENCES `cw_portal`.`supervisor_example` (`project_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`supervisor_diff`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`supervisor_diff` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `diff_type` INT(11) NOT NULL,
  `person_id` INT(11) NULL DEFAULT NULL,
  `project_id` INT(11) NULL DEFAULT NULL,
  `details` LONGTEXT NULL DEFAULT NULL,
  `when` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `supervisor_diff_16f39487` (`person_id` ASC) VISIBLE,
  INDEX `supervisor_diff_37952554` (`project_id` ASC) VISIBLE,
  CONSTRAINT `person_id_refs_id_e6c3c67a`
    FOREIGN KEY (`person_id`)
    REFERENCES `cw_portal`.`studentportal_customuser` (`id`),
  CONSTRAINT `project_id_refs_id_678190fe`
    FOREIGN KEY (`project_id`)
    REFERENCES `cw_portal`.`studentportal_project` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 11758
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`supervisor_like`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`supervisor_like` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `project_id` INT(11) NOT NULL,
  `liked_by_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `supervisor_like_37952554` (`project_id` ASC) VISIBLE,
  INDEX `supervisor_like_751d22e6` (`liked_by_id` ASC) VISIBLE,
  CONSTRAINT `liked_by_id_refs_id_4cda879d`
    FOREIGN KEY (`liked_by_id`)
    REFERENCES `cw_portal`.`studentportal_customuser` (`id`),
  CONSTRAINT `project_id_refs_project_id_6c855ad4`
    FOREIGN KEY (`project_id`)
    REFERENCES `cw_portal`.`supervisor_example` (`project_id`))
ENGINE = InnoDB
AUTO_INCREMENT = 15
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`supervisor_news`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`supervisor_news` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `content` LONGTEXT NOT NULL,
  `date_created` DATETIME NOT NULL,
  `priority` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`supervisor_notification`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`supervisor_notification` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `noti_type` INT(11) NULL DEFAULT NULL,
  `project_id` INT(11) NULL DEFAULT NULL,
  `NGO_name` VARCHAR(200) NOT NULL,
  `NGO_link` VARCHAR(200) NOT NULL,
  `NGO_details` LONGTEXT NOT NULL,
  `NGO_sugg_by_id` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `supervisor_notification_37952554` (`project_id` ASC) VISIBLE,
  INDEX `supervisor_notification_29fe79c7` (`NGO_sugg_by_id` ASC) VISIBLE,
  CONSTRAINT `NGO_sugg_by_id_refs_id_ddc22b7d`
    FOREIGN KEY (`NGO_sugg_by_id`)
    REFERENCES `cw_portal`.`studentportal_customuser` (`id`),
  CONSTRAINT `project_id_refs_id_4dedc7c1`
    FOREIGN KEY (`project_id`)
    REFERENCES `cw_portal`.`studentportal_project` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 2583
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `cw_portal`.`supervisor_ta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cw_portal`.`supervisor_ta` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(100) NOT NULL,
  `instructor` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 25
DEFAULT CHARACTER SET = latin1;


CREATE TABLE IF NOT EXISTS `cw_portal`.`supervisor_flag` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `key` VARCHAR(100) NOT NULL,
    `value` tinyint(1) NOT NULL,
    PRIMARY KEY (`id`)
)
DEFAULT CHARACTER SET = latin1;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- Adding options
INSERT INTO `cw_portal`.`studentportal_category`
(`name`,
`description`)
VALUES
("SG",
"Self Growth");

INSERT INTO `cw_portal`.`studentportal_category`
(`name`,
`description`)
VALUES
("CW",
"Community Work");

INSERT INTO `cw_portal`.`supervisor_flag`
(`key`,
`value`)
VALUES
("add_project",
1);
