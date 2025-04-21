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

Template for populating the DB:
````
```
-- Inserting data into Coach table
INSERT INTO Coach (Name, Surname, Gender, DateOfBirth, Experience)
VALUES ('Іван', 'Петренко', 'Male', '1980-05-15', '15 років досвіду'),
       ('Олена', 'Сидоренко', 'Female', '1985-11-20', '10 років досвіду'),
       ('Андрій', 'Коваленко', 'Male', '1978-03-01', '18 років досвіду'),
       ('Тетяна', 'Лисенко', 'Female', '1990-07-22', '5 років досвіду');

-- Inserting data into Group_ table
INSERT INTO Group_ (Name, Address, CoachID)
VALUES ('Lviv Dolphins', 'вул. Симоненка, 10, Львів', 1),
       ('Kyiv Sharks', 'пр. Перемоги, 50, Київ', 2),
       ('Odesa Waves', 'Аркадія, пляж №7, Одеса', 3),
       ('Kharkiv Rockets', 'вул. Клочківська, 47, Харків', 4);

-- Inserting data into Facility table
INSERT INTO Facility (Name, Address, Distance, LinesAmount)
VALUES ('СК "Водан"', 'вул. Симоненка, 10, Львів', 25.00, 8),
       ('Басейн "Олімпійський"', 'пр. Перемоги, 50, Київ', 50.00, 10),
       ('СК "Чорноморець"', 'Аркадія, пляж №7, Одеса', 25.00, 6),
       ('Басейн "Динамо"', 'вул. Клочківська, 47, Харків', 25.00, 7);

-- Inserting data into Timeslot table
INSERT INTO Timeslot (FacilityID, StartTime, EndTime)
VALUES (1, '2025-05-01 09:00:00', '2025-05-01 11:00:00'),
       (1, '2024-05-01 16:00:00', '2024-05-01 18:00:00'),
       (2, '2024-05-02 10:00:00', '2024-05-02 12:00:00'),
       (3, '2025-05-03 14:00:00', '2025-05-03 16:00:00'),
       (4, '2025-05-04 17:00:00', '2025-05-04 19:00:00');

-- Inserting data into Event table
INSERT INTO Event (Name, Type, TimeslotID)
VALUES ('Весняні надії 2025', 'Competition', 1),         -- Future event
       ('Тренування з брасу', 'Training', 2),            -- Past event
       ('Кубок Чорного моря', 'Competition', 3),         -- Past event
       ('Інтенсив з кролю', 'Training', 4),              -- Future event
       ('Підготовка до літнього чемпіонату', 'Training', 1);  -- Past event

-- Inserting data into Swimmer table
INSERT INTO Swimmer (Name, Surname, Gender, DateOfBirth, GroupID)
VALUES ('Марія', 'Шевченко', 'Female', '2003-08-10', 1),
       ('Олександр', 'Мороз', 'Male', '2002-12-05', 1),
       ('Анна', 'Василенко', 'Female', '2004-04-25', 2),
       ('Дмитро', 'Павлов', 'Male', '2001-09-01', 2),
       ('Софія', 'Іванова', 'Female', '2005-01-15', 3),
       ('Артем', 'Захарчук', 'Male', '2003-06-30', 3),
       ('Вікторія', 'Бондаренко', 'Female', '2004-11-12', 4),
       ('Максим', 'Ткаченко', 'Male', '2002-07-01', 4);

-- Inserting data into Style table
INSERT INTO Style (Style)
VALUES ('Кроль'),
       ('Брас'),
       ('Баттерфляй'),
       ('На спині');

-- Inserting data into Swim table
INSERT INTO Swim (Distance, Duration, EventID, CoachID, StyleID)
VALUES (50.00, 30, 1, 1, 1),         -- Future event
       (100.00, 65, 1, 2, 2),        -- Future event
       (50.00, 35, 3, 3, 1),         -- Past event
       (200.00, 130, 3, 1, 3),       -- Past event
       (50.00, 40, 2, 2, 2),         -- Past event
       (100.00, 70, 4, 4, 1),        -- Future event
       (50.00, 32, 1, 1, 4),         -- Future event
       (100.00, 68, 3, 3, 2);        -- Past event

-- Inserting data into Result table (For past events)
INSERT INTO Result (Length, Time, EventID, SwimmerID, StyleID)
VALUES (50.00, 34, 3, 5, 1),         -- Past event
       (50.00, 36, 3, 6, 1),         -- Past event
       (200.00, 128, 3, 7, 3),       -- Past event
       (200.00, 132, 3, 8, 3),       -- Past event
       (50.00, 39, 2, 1, 2),         -- Past event
       (50.00, 41, 2, 3, 2),         -- Past event
       (100.00, 67, 3, 1, 2),        -- Past event
       (100.00, 69, 3, 3, 2);        -- Past event

-- Inserting data into SwimmerStyle junction table
INSERT INTO SwimmerStyle (SwimmerID, StyleID)
VALUES (1, 1),
       (1, 2),
       (2, 1),
       (2, 4),
       (3, 2),
       (3, 3),
       (4, 1),
       (4, 2),
       (4, 3),
       (4, 4),
       (5, 1),
       (6, 1),
       (6, 4),
       (7, 3),
       (8, 1),
       (8, 3);

-- Inserting data into EventSwimmer junction table
INSERT INTO EventSwimmer (EventID, SwimmerID)
VALUES (1, 1),
       (1, 2),
       (1, 3),
       (1, 4),
       (1, 5),
       (1, 7),
       (3, 5),
       (3, 6),
       (3, 7),
       (3, 8),
       (3, 1),
       (3, 3),
       (2, 1),
       (2, 3),
       (4, 5),
       (4, 7),
       (5, 2),
       (5, 4),
       (5, 6),
       (5, 8);

-- Inserting data into FacilityCoach junction table
INSERT INTO FacilityCoach (FacilityID, CoachID)
VALUES (1, 1),
       (1, 2),
       (2, 2),
       (2, 3),
       (3, 3),
       (4, 4),
       (4, 1);
```
````

Note, that this app **does not realise** all the functionality needed for "Lviv Swimmng Association", but realises sufficient one.