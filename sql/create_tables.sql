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

DROP TABLE IF EXISTS sector_names;

CREATE TABLE sector_names(
    sector TEXT PRIMARY KEY,
    name TEXT
);

INSERT INTO sector_names(sector,name) VALUES 
('11','Agriculture, Forestry, Fishing and Hunting'),
('21','Mining, Quarrying, and Oil and Gas Extraction'),
('22','Utilities'),
('23','Construction'),
('31', 'Manufacturing'),
('42', 'Wholesale Trade'),
('44', 'Retail Trade'),
('48', 'Transportation and Warehousing'),
('51', 'Information'),
('52', 'Finance and Insurance'),
('53', 'Real Estate and Rental and Leasing'),
('54', 'Professional, Scientific, and Technical Services'),
('55',	'Management of Companies and Enterprises'),
('56',	'Administrative and Support and Waste Management'),
('61',	'Educational Services'),
('62',	'Health Care and Social Assistance'),
('71',	'Arts, Entertainment, and Recreation'),
('72',	'Accommodation and Food Services'),
('81',	'Other Services (except Public Administration)'),
('XX',	'Multi-sector or multi-state companies');
