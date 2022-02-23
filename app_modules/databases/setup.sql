/* Add societies */
INSERT INTO society (name, address, pin_code) VALUES ("Esser Residency", "Majhipara, Dashadrone", 700136);
INSERT INTO society (name, address, pin_code) VALUES ("Tirath Abasan", "Majhipara, Dashadrone", 700136);

INSERT INTO user (name, email, phone, role_id, password) VALUES ("Admin", "admin@email.com", "1000000000", 1, "gAAAAABhQy4pQL4IzVodeeJMk_91ZKaUl8gqsaHo5HBR4B725uk9ydyZ5ikGr4x7lPidfrmgYBwCrhmos1t9X3XqkUD_aM8xyA==");
INSERT INTO user (name, email, phone, role_id, password) VALUES ("User", "user@email.com", "1000000000", 2, "gAAAAABhRKU2_EnRp0hVjZD5KVJ9UTL_IphIURj0OsBH-0npovp3CTqhMkdwMG13Igsh4zA_a7S7qG2uWT8q7YHh-YDEkIBxeA==");

/* Add User Role */
INSERT INTO user_role("role") VALUES ("Admin");
INSERT INTO user_role("role") VALUES ("User");

/* Add Flat */
INSERT INTO flat(flat_code, balance, owner_id) VALUES ("1A", 0, 1);
/* Add Member */
INSERT INTO member(society_id, user_id, flat_id) VALUES (1, 1, 1);