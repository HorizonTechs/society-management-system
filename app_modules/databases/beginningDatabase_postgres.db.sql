set transaction read write; 
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "country_currency" (
	"id"	INTEGER NOT NULL,
	"country_name"	VARCHAR(50),
	"currency_name"	VARCHAR(50),
	"currency_code"	VARCHAR(3),
	PRIMARY KEY("id"),
	UNIQUE("country_name")
);
CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER NOT NULL,
	"uuid"	VARCHAR(50),
	"name"	VARCHAR(100) NOT NULL,
	"email"	VARCHAR(50) NOT NULL,
	"phone"	VARCHAR(14),
	"last_logged_in"	DATE,
	PRIMARY KEY("id"),
	UNIQUE("phone"),
	UNIQUE("email"),
	UNIQUE("uuid")
);
CREATE TABLE IF NOT EXISTS "security_question" (
	"id"	INTEGER NOT NULL,
	"question"	VARCHAR(120),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "account_type" (
	"id"	INTEGER NOT NULL,
	"account_type"	VARCHAR(50) NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "collection_type" (
	"id"	INTEGER NOT NULL,
	"type"	VARCHAR(20) NOT NULL,
	PRIMARY KEY("id"),
	UNIQUE("type")
);
CREATE TABLE IF NOT EXISTS "payment_method" (
	"id"	INTEGER NOT NULL,
	"method"	VARCHAR(20) NOT NULL,
	UNIQUE("method"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "user_role" (
	"id"	INTEGER NOT NULL,
	"role"	VARCHAR(20) NOT NULL,
	UNIQUE("role"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "society" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(120) NOT NULL,
	"address"	VARCHAR(120) NOT NULL,
	"pin_code"	INTEGER NOT NULL,
	"country_currency_id"	INTEGER NOT NULL,
	FOREIGN KEY("country_currency_id") REFERENCES "country_currency"("id"),
	UNIQUE("name","address","pin_code"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "password_manager" (
	"id"	INTEGER NOT NULL,
	"password"	VARCHAR(120) NOT NULL,
	"user_id"	INTEGER,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	UNIQUE("user_id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "role_manager" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"society_id"	INTEGER,
	"role_id"	INTEGER,
	FOREIGN KEY("role_id") REFERENCES "user_role"("id"),
	FOREIGN KEY("society_id") REFERENCES "society"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	UNIQUE("user_id","society_id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "flat" (
	"id"	INTEGER NOT NULL,
	"society_id"	INTEGER NOT NULL,
	"flat_code"	VARCHAR(10) NOT NULL,
	"area"	INTEGER NOT NULL,
	FOREIGN KEY("society_id") REFERENCES "society"("id"),
	UNIQUE("society_id","flat_code"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "collection" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(120) NOT NULL,
	"society_id"	INTEGER NOT NULL,
	"type_id"	INTEGER NOT NULL,
	"rate"	INTEGER NOT NULL,
	"fixed"	BOOLEAN NOT NULL,
	"balance"	INTEGER NOT NULL,
	"collection_start_date"	DATE NOT NULL,
	FOREIGN KEY("type_id") REFERENCES "collection_type"("id"),
	FOREIGN KEY("society_id") REFERENCES "society"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "member" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"flat_id"	INTEGER NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	FOREIGN KEY("flat_id") REFERENCES "flat"("id"),
	UNIQUE("user_id","flat_id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "flat_owner" (
	"id"	INTEGER NOT NULL,
	"member_id"	INTEGER,
	FOREIGN KEY("member_id") REFERENCES "member"("id"),
	UNIQUE("member_id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "account" (
	"id"	INTEGER NOT NULL,
	"account_type_id"	INTEGER NOT NULL,
	"owner_id"	INTEGER,
	"due_amount"	INTEGER NOT NULL,
	FOREIGN KEY("account_type_id") REFERENCES "account_type"("id"),
	FOREIGN KEY("owner_id") REFERENCES "flat_owner"("id"),
	UNIQUE("owner_id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "transaction_log" (
	"id"	INTEGER NOT NULL,
	"sender_id"	INTEGER,
	"receiver_id"	INTEGER,
	"amount"	INTEGER NOT NULL,
	"date"	DATE NOT NULL,
	"method_id"	INTEGER NOT NULL,
	FOREIGN KEY("method_id") REFERENCES "payment_method"("id"),
	FOREIGN KEY("sender_id") REFERENCES "account"("id"),
	FOREIGN KEY("receiver_id") REFERENCES "account"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "income" (
	"id"	INTEGER NOT NULL,
	"owner_id"	INTEGER NOT NULL,
	"expected_amount"	INTEGER NOT NULL,
	"transaction_id"	INTEGER,
	"collection_id"	INTEGER NOT NULL,
	FOREIGN KEY("collection_id") REFERENCES "collection"("id"),
	FOREIGN KEY("owner_id") REFERENCES "flat_owner"("id"),
	FOREIGN KEY("transaction_id") REFERENCES "transaction_log"("id"),
	UNIQUE("collection_id","owner_id"),
	UNIQUE("transaction_id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "expense" (
	"id"	INTEGER NOT NULL,
	"collection_id"	INTEGER NOT NULL,
	"transaction_id"	INTEGER NOT NULL,
	FOREIGN KEY("collection_id") REFERENCES "collection"("id"),
	FOREIGN KEY("transaction_id") REFERENCES "transaction_log"("id"),
	UNIQUE("transaction_id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "transaction_comment" (
	"id"	INTEGER NOT NULL,
	"comment"	VARCHAR(200),
	"transaction_id"	INTEGER NOT NULL,
	FOREIGN KEY("transaction_id") REFERENCES "transaction_log"("id"),
	UNIQUE("transaction_id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "user_question_answer" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"question_id"	INTEGER NOT NULL,
	"answer"	VARCHAR(120) NOT NULL,
	FOREIGN KEY("question_id") REFERENCES "security_question"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	PRIMARY KEY("id")
);
INSERT INTO "country_currency" ("id","country_name","currency_name","currency_code") VALUES (1,'Afghanistan','Afghan afghani','AFN'),
 (2,'Albania','Albanian lek','ALL'),
 (3,'Algeria','Algerian dinar','DZD'),
 (4,'Andorra','Euro','EUR'),
 (5,'Angola','Angolan kwanza','AOA'),
 (6,'Antigua and Barbuda','East Caribbean dollar','XCD'),
 (7,'Argentina','Argentine peso','ARS'),
 (8,'Armenia','Armenian dram','AMD'),
 (9,'Australia','Australian dollar','AUD'),
 (10,'Austria','Euro','EUR'),
 (11,'Azerbaijan','Azerbaijani manat','AZN'),
 (12,'Bahamas','Bahamian dollar','BSD'),
 (13,'Bahrain','Bahraini dinar','BHD'),
 (14,'Bangladesh','Bangladeshi taka','BDT'),
 (15,'Barbados','Barbadian dollar','BBD'),
 (16,'Belarus','Belarusian ruble','BYN'),
 (17,'Belgium','Euro','EUR'),
 (18,'Belize','Belize dollar','BZD'),
 (19,'Benin','West African CFA franc','XOF'),
 (20,'Bhutan','Bhutanese ngultrum','BTN'),
 (21,'Bolivia','Bolivian boliviano','BOB'),
 (22,'Bosnia and Herzegovina','Bosnia and Herzegovina convertible mark','BAM'),
 (23,'Botswana','Botswana pula','BWP'),
 (24,'Brazil','Brazilian real','BRL'),
 (25,'Brunei','Brunei dollar','BND'),
 (26,'Bulgaria','Bulgarian lev','BGN'),
 (27,'Burkina Faso','West African CFA franc','XOF'),
 (28,'Burundi','Burundian franc','BIF'),
 (29,'Cambodia','Cambodian riel','KHR'),
 (30,'Cameroon','Central African CFA franc','XAF'),
 (31,'Canada','Canadian dollar','CAD'),
 (32,'Cape Verde','Cape Verdean escudo','CVE'),
 (33,'Central African Republic','Central African CFA franc','XAF'),
 (34,'Chad','Central African CFA franc','XAF'),
 (35,'Chile','Chilean peso','CLP'),
 (36,'China','Chinese yuan','CNY'),
 (37,'Colombia','Colombian peso','COP'),
 (38,'Comoros','Comorian franc','KMF'),
 (39,'Costa Rica','Costa Rican colón','CRC'),
 (40,'Croatia','Croatian kuna','HRK'),
 (41,'Cuba','Cuban peso','CUP'),
 (42,'Cyprus','Euro','EUR'),
 (43,'Czech Republic','Czech koruna','CZK'),
 (44,'Democratic Republic of Congo','Congolese franc','CDF'),
 (45,'Denmark','Danish krone','DKK'),
 (46,'Djibouti','Djiboutian franc','DJF'),
 (47,'Dominica','East Caribbean dollar','XCD'),
 (48,'Dominican Republic','Dominican peso','DOP'),
 (49,'East Timor','United States dollar','USD'),
 (50,'Ecuador','United States dollar','USD'),
 (51,'Egypt','Egyptian pound','EGP'),
 (52,'El Salvador','United States dollar','USD'),
 (53,'Equatorial Guinea','Central African CFA franc','XAF'),
 (54,'Eritrea','Eritrean nakfa','ERN'),
 (55,'Estonia','Euro','EUR'),
 (56,'Eswatini','Swazi lilangeni','SZL'),
 (57,'Ethiopia','Ethiopian birr','ETB'),
 (58,'Fiji','Fijian dollar','FJD'),
 (59,'Finland','Euro','EUR'),
 (60,'France','Euro','EUR'),
 (61,'Gabon','Central African CFA franc','XAF'),
 (62,'Gambia','Gambian dalasi','GMD'),
 (63,'Georgia','Georgian lari','GEL'),
 (64,'Germany','Euro','EUR'),
 (65,'Ghana','Ghanaian cedi','GHS'),
 (66,'Greece','Euro','EUR'),
 (67,'Grenada','East Caribbean dollar','XCD'),
 (68,'Guatemala','Guatemalan quetzal','GTQ'),
 (69,'Guinea','Guinean franc','GNF'),
 (70,'Guinea-Bissau','West African CFA franc','XOF'),
 (71,'Guyana','Guyanese dollar','GYD'),
 (72,'Haiti','Haitian gourde','HTG'),
 (73,'Honduras','Honduran lempira','HNL'),
 (74,'Hungary','Hungarian forint','HUF'),
 (75,'Iceland','Icelandic króna','ISK'),
 (76,'India','Indian rupee','INR'),
 (77,'Indonesia','Indonesian rupiah','IDR'),
 (78,'Iran','Iranian rial','IRR'),
 (79,'Iraq','Iraqi dinar','IQD'),
 (80,'Ireland','Euro','EUR'),
 (81,'Israel','Israeli new shekel','ILS'),
 (82,'Italy','Euro','EUR'),
 (83,'Ivory Coast','West African CFA franc','XOF'),
 (84,'Jamaica','Jamaican dollar','JMD'),
 (85,'Japan','Japanese yen','JPY'),
 (86,'Jordan','Jordanian dinar','JOD'),
 (87,'Kazakhstan','Kazakhstani tenge','KZT'),
 (88,'Kenya','Kenyan shilling','KES'),
 (89,'Kiribati','Australian dollar','AUD'),
 (90,'Korea, North','North Korean won','KPW'),
 (91,'Korea, South','South Korean won','KRW'),
 (92,'Kosovo','Euro','EUR'),
 (93,'Kuwait','Kuwaiti dinar','KWD'),
 (94,'Kyrgyzstan','Kyrgyzstani som','KGS'),
 (95,'Laos','Lao kip','LAK'),
 (96,'Latvia','Euro','EUR'),
 (97,'Lebanon','Lebanese pound','LBP'),
 (98,'Lesotho','Lesotho loti','LSL'),
 (99,'Liberia','Liberian dollar','LRD'),
 (100,'Libya','Libyan dinar','LYD'),
 (101,'Liechtenstein','Swiss franc','CHF'),
 (102,'Lithuania','Euro','EUR'),
 (103,'Luxembourg','Euro','EUR'),
 (104,'Madagascar','Malagasy ariary','MGA'),
 (105,'Malawi','Malawian kwacha','MWK'),
 (106,'Malaysia','Malaysian ringgit','MYR'),
 (107,'Maldives','Maldivian rufiyaa','MVR'),
 (108,'Mali','West African CFA franc','XOF'),
 (109,'Malta','Euro','EUR'),
 (110,'Marshall Islands','United States dollar','USD'),
 (111,'Mauritania','Mauritanian ouguiya','MRO'),
 (112,'Mauritius','Mauritian rupee','MUR'),
 (113,'Mexico','Mexican peso','MXN'),
 (114,'Micronesia','United States dollar','USD'),
 (115,'Moldova','Moldovan leu','MDL'),
 (116,'Monaco','Euro','EUR'),
 (117,'Mongolia','Mongolian tögrög','MNT'),
 (118,'Montenegro','Euro','EUR'),
 (119,'Morocco','Moroccan dirham','MAD'),
 (120,'Mozambique','Mozambican metical','MZN'),
 (121,'Myanmar','Burmese kyat','MMK'),
 (122,'Namibia','Namibian dollar','NAD'),
 (123,'Nauru','Australian dollar','AUD'),
 (124,'Nepal','Nepalese rupee','NPR'),
 (125,'Netherlands','Euro','EUR'),
 (126,'New Zealand','New Zealand dollar','NZD'),
 (127,'Nicaragua','Nicaraguan córdoba','NIO'),
 (128,'Niger','West African CFA franc','XOF'),
 (129,'Nigeria','Nigerian naira','NGN'),
 (130,'North Macedonia','Macedonian denar','MKD'),
 (131,'Norway','Norwegian krone','NOK'),
 (132,'Oman','Omani rial','OMR'),
 (133,'Pakistan','Pakistani rupee','PKR'),
 (134,'Palau','United States dollar','USD'),
 (135,'Palestine','Israeli new shekel','ILS'),
 (136,'Panama','Panamanian balboa','PAB'),
 (137,'Papua New Guinea','Papua New Guinean kina','PGK'),
 (138,'Paraguay','Paraguayan guaraní','PYG'),
 (139,'Peru','Peruvian sol','PEN'),
 (140,'Philippines','Philippine peso','PHP'),
 (141,'Poland','Polish zloty','PLN'),
 (142,'Portugal','Euro','EUR'),
 (143,'Qatar','Qatari riyal','QAR'),
 (144,'Republic of the Congo','Central African CFA franc','XAF'),
 (145,'Romania','Romanian leu','RON'),
 (146,'Russia','Russian ruble','RUB'),
 (147,'Rwanda','Rwandan franc','RWF'),
 (148,'Saint Kitts and Nevis','East Caribbean dollar','XCD'),
 (149,'Saint Lucia','East Caribbean dollar','XCD'),
 (150,'Saint Vincent and the Grenadines','East Caribbean dollar','XCD'),
 (151,'Samoa','Samoan tala','WST'),
 (152,'San Marino','Euro','EUR'),
 (153,'São Tomé and Príncipe','São Tomé and Príncipe dobra','STD'),
 (154,'Saudi Arabia','Saudi riyal','SAR'),
 (155,'Senegal','West African CFA franc','XOF'),
 (156,'Serbia','Serbian dinar','RSD'),
 (157,'Seychelles','Seychellois rupee','SCR'),
 (158,'Sierra Leone','Sierra Leonean leone','SLL'),
 (159,'Singapore','Singapore dollar','SGD'),
 (160,'Slovakia','Euro','EUR'),
 (161,'Slovenia','Euro','EUR'),
 (162,'Solomon Islands','Solomon Islands dollar','SBD'),
 (163,'Somalia','Somali shilling','SOS'),
 (164,'South Africa','South African rand','ZAR'),
 (165,'South Sudan','South Sudanese pound','SSP'),
 (166,'Spain','Euro','EUR'),
 (167,'Sri Lanka','Sri Lankan rupee','LKR'),
 (168,'Sudan','Sudanese pound','SDG'),
 (169,'Suriname','Surinamese dollar','SRD'),
 (170,'Sweden','Swedish krona','SEK'),
 (171,'Switzerland','Swiss franc','CHF'),
 (172,'Syria','Syrian pound','SYP'),
 (173,'Taiwan','New Taiwan dollar','TWD'),
 (174,'Tajikistan','Tajikistani somoni','TJS'),
 (175,'Tanzania','Tanzanian shilling','TZS'),
 (176,'Thailand','Thai baht','THB'),
 (177,'Togo','West African CFA franc','XOF'),
 (178,'Tonga','Tongan pa''anga','TOP'),
 (179,'Trinidad and Tobago','Trinidad and Tobago dollar','TTD'),
 (180,'Tunisia','Tunisian dinar','TND'),
 (181,'Turkey','Turkish lira','TRY'),
 (182,'Turkmenistan','Turkmenistan manat','TMT'),
 (183,'Tuvalu','Australian dollar','AUD'),
 (184,'Uganda','Ugandan shilling','UGX'),
 (185,'Ukraine','Ukrainian hryvnia','UAH'),
 (186,'United Arab Emirates','United Arab Emirates dirham','AED'),
 (187,'United Kingdom','British pound','GBP'),
 (188,'United States','United States dollar','USD'),
 (189,'Uruguay','Uruguayan peso','UYU'),
 (190,'Uzbekistan','Uzbekistani som','UZS'),
 (191,'Vanuatu','Vanuatu vatu','VUV'),
 (192,'Vatican City','Euro','EUR'),
 (193,'Venezuela','Venezuelan bolívar','VEF'),
 (194,'Vietnam','Vietnamese dong','VND'),
 (195,'Yemen','Yemeni rial','YER'),
 (196,'Zambia','Zambian kwacha','ZMW'),
 (197,'Zimbabwe','United States dollar','USD');
INSERT INTO "user" ("id","uuid","name","email","phone","last_logged_in") VALUES (1,'37683cce-e44b-4f55-b8d4-6de3d46f2d12','Master','master@email.com','1234567890','2022-02-21 10:47:25.607906'),
 (2,'350be8ce-447f-422e-8903-185f63fa1272','Admin','admin@email.com','12341515111','2022-02-21 19:22:36.070993'),
 (3,'29b0ea48-c0b1-4db4-8331-3b931b59d2e6','User','user@email.com','123415123311','2022-02-21 16:12:07.627662');
INSERT INTO "security_question" ("id","question") VALUES (1,'What is the name of your favorite pet?'),
 (2,'What high school did you attend?'),
 (3,'What is the name of your first school?'),
 (4,'What was the make of your first car?'),
 (5,'What was your favorite food as a child?'),
 (6,'When is your Birthday?'),
 (7,'In what city or town did your parents meet?');
INSERT INTO "account_type" ("id","account_type") VALUES (1,'Owner'),
 (2,'System'),
 (3,'All Owners'),
 (4,'Miscellaneous'),
 (5,'Security'),
 (6,'Electricity'),
 (7,'Sweeper');
INSERT INTO "account" ("id","account_type_id","owner_id","due_amount") VALUES (1,2,NULL,0),
 (2,3,NULL,0),
 (3,4,NULL,0),
 (4,5,NULL,0),
 (5,6,NULL,0),
 (6,7,NULL,0);
INSERT INTO "collection_type" ("id","type") VALUES (1,'Monthly'),
 (2,'Festive'),
 (3,'Emergency');
INSERT INTO "payment_method" ("id","method") VALUES (1,'Internal'),
 (2,'Cash'),
 (3,'Google Pay'),
 (4,'Phone Pe'),
 (5,'Paytm'),
 (6,'UPI'),
 (7,'IMPS'),
 (8,'Other');
INSERT INTO "user_role" ("id","role") VALUES (1,'Master'),
 (2,'Admin'),
 (3,'User');
INSERT INTO "password_manager" ("id","password","user_id") VALUES (1,'sha256$HV3q1tBoq40y7L4h$3dab967e303cd55b0db894228ac32f899846ed615851f8ab29b0b93b67c7dcd8',1),
 (2,'sha256$VqsGtqPXmiXOrHET$1cc5c5a9ebf5768c8993e23262fd44a945fc248c32c8fc08f86ca46225dfd426',2),
 (3,'sha256$keNXKAeEbOuggP5D$7f0c4781752624faaec3e05d5cf3492a177762f0a2d0cd386410ad82fd03cf1d',3);
INSERT INTO "role_manager" ("id","user_id","society_id","role_id") VALUES (1,1,NULL,1);
COMMIT;