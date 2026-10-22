DROP TABLE IF EXISTS national;

CREATE TABLE National(Question_ID INT,
Question TEXT,
Answer_ID INT,
Answer varchar(100),
cycle TEXT,
value varchar(100),
percentage FLOAT,
status VARCHAR(50),
period_start DATE,
period_end DATE
);

DROP TABLE IF EXISTS sector;

CREATE TABLE Sector(sector TEXT,
Question_ID INT,
Question TEXT,
Answer_ID INT,
Answer varchar(100),
cycle TEXT,
value varchar(100),
percentage FLOAT,
status VARCHAR(50),
period_start DATE,
period_end DATE
);