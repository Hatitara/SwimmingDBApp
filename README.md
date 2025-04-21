The app for HW3 of DB course. Follows the DDL of DBS:

````
```
DROP DATABASE IF EXISTS swimming;
CREATE DATABASE IF NOT EXISTS swimming
    CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci';
USE swimming;

-- ======================== MAIN TABLES ========================

DROP TABLE IF EXISTS `Group_`;
CREATE TABLE `Group_`
(
    GroupID INT AUTO_INCREMENT PRIMARY KEY,
    Name    VARCHAR(255) NOT NULL,
    Address VARCHAR(255) NOT NULL
) ENGINE = InnoDB COMMENT ='Group entity type.';

DROP TABLE IF EXISTS Facility;
CREATE TABLE Facility
(
    FacilityID  INT AUTO_INCREMENT PRIMARY KEY,
    Name        VARCHAR(255)   NOT NULL,
    Address     VARCHAR(255)   NOT NULL,
    Distance    DECIMAL(10, 2) NOT NULL,
    LinesAmount INT            NOT NULL
) ENGINE = InnoDB COMMENT ='Facility entity type.';

DROP TABLE IF EXISTS Timeslot;
CREATE TABLE Timeslot
(
    TimeslotID INT AUTO_INCREMENT PRIMARY KEY,
    FacilityID INT      NOT NULL,
    StartTime  DATETIME NOT NULL,
    EndTime    DATETIME NOT NULL,
    FOREIGN KEY (FacilityID) REFERENCES Facility (FacilityID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT ='Timeslot entity type.';

DROP TABLE IF EXISTS Event;
CREATE TABLE Event
(
    EventID    INT AUTO_INCREMENT PRIMARY KEY,
    Name       VARCHAR(100)                     NOT NULL,
    Type       ENUM ('Competition', 'Training') NOT NULL,
    TimeslotID INT                              NOT NULL,
    FOREIGN KEY (TimeslotID) REFERENCES Timeslot (TimeslotID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT ='Event entity type.';

DROP TABLE IF EXISTS Coach;
CREATE TABLE Coach
(
    CoachID     INT AUTO_INCREMENT PRIMARY KEY,
    Name        VARCHAR(255)                     NOT NULL,
    Surname     VARCHAR(255)                     NOT NULL,
    Gender      ENUM ('Male', 'Female', 'Other') NOT NULL,
    DateOfBirth DATE                             NOT NULL,
    Experience  TEXT
) ENGINE = InnoDB COMMENT ='Coach entity type.';

DROP TABLE IF EXISTS Swimmer;
CREATE TABLE Swimmer
(
    SwimmerID   INT AUTO_INCREMENT PRIMARY KEY,
    Name        VARCHAR(255)                     NOT NULL,
    Surname     VARCHAR(255)                     NOT NULL,
    Gender      ENUM ('Male', 'Female', 'Other') NOT NULL,
    DateOfBirth DATE                             NOT NULL,
    GroupID     INT,
    FOREIGN KEY (GroupID) REFERENCES Group_ (GroupID)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT ='Swimmer entity type.';

DROP TABLE IF EXISTS Style;
CREATE TABLE Style
(
    StyleID INT AUTO_INCREMENT PRIMARY KEY,
    Style   VARCHAR(100) UNIQUE NOT NULL
) ENGINE = InnoDB COMMENT ='Style entity type.';

DROP TABLE IF EXISTS Swim;
CREATE TABLE Swim
(
    SwimID   INT AUTO_INCREMENT PRIMARY KEY,
    Distance DECIMAL(10, 2) NOT NULL,
    Duration INT            NOT NULL,
    EventID  INT,
    CoachID  INT,
    StyleID  INT            NOT NULL,
    FOREIGN KEY (EventID) REFERENCES Event (EventID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (CoachID) REFERENCES Coach (CoachID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (StyleID) REFERENCES Style (StyleID)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT ='Swim entity.';

DROP TABLE IF EXISTS Result;
CREATE TABLE Result
(
    ResultID  INT AUTO_INCREMENT PRIMARY KEY,
    Length    DECIMAL(10, 2) NOT NULL,
    Time      INT            NOT NULL,
    EventID   INT            NOT NULL,
    SwimmerID INT            NOT NULL,
    StyleID   INT            NOT NULL,
    FOREIGN KEY (EventID) REFERENCES Event (EventID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (SwimmerID) REFERENCES Swimmer (SwimmerID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (StyleID) REFERENCES Style (StyleID)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT ='Result entity.';

-- ======================== JUNCTION TABLES ========================

DROP TABLE IF EXISTS SwimmerStyle;
CREATE TABLE SwimmerStyle
(
    SwimmerID INT NOT NULL,
    StyleID   INT NOT NULL,
    PRIMARY KEY (SwimmerID, StyleID),
    FOREIGN KEY (SwimmerID) REFERENCES Swimmer (SwimmerID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (StyleID) REFERENCES Style (StyleID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT ='Swimmer - Style relationship.';

DROP TABLE IF EXISTS EventSwimmer;
CREATE TABLE EventSwimmer
(
    EventID   INT NOT NULL,
    SwimmerID INT NOT NULL,
    PRIMARY KEY (EventID, SwimmerID),
    FOREIGN KEY (EventID) REFERENCES Event (EventID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (SwimmerID) REFERENCES Swimmer (SwimmerID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT ='Event - Swimmer participation.';

DROP TABLE IF EXISTS FacilityCoach;
CREATE TABLE FacilityCoach
(
    FacilityID INT NOT NULL,
    CoachID    INT NOT NULL,
    PRIMARY KEY (FacilityID, CoachID),
    FOREIGN KEY (FacilityID) REFERENCES Facility (FacilityID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (CoachID) REFERENCES Coach (CoachID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT ='Coach - Facility assignment.';

-- ======================== HOT FIX ========================

ALTER TABLE Group_
    ADD COLUMN CoachID INT NOT NULL,
    ADD CONSTRAINT fk_group_coach
        FOREIGN KEY (CoachID) REFERENCES Coach (CoachID)
            ON DELETE CASCADE ON UPDATE CASCADE;

```
````