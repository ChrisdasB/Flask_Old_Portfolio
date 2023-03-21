PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE comments (
comment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
user_id INTEGER NOT NULL,
timestamp TEXT,
text TEXT NOT NULL,
FOREIGN KEY (user_id)
	REFERENCES users (user_id)
);
INSERT INTO comments VALUES(28,1,'2023-03-01 23:08:11.471549','I am the admin. I have the power!');
INSERT INTO comments VALUES(29,2,'2023-03-02 17:37:21.479767','Hello, this is an awesome site!');
INSERT INTO comments VALUES(32,1,'2023-03-02 18:31:09.523355','Hello, this is a German comment!');
CREATE TABLE users (
user_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL,
hash TEXT NOT NULL,
reg_date TEXT,
log_date TEXT
);
INSERT INTO users VALUES(1,'Admin','pbkdf2:sha256:260000$POkfNNTerm00r653$213e77a6b19c12eb4a6113753c38ccc651582feb9fb97d338e2171d8a336b47d','2023-02-24 12:44:38','2023-03-02 19:09:36');
INSERT INTO users VALUES(2,'Chris','pbkdf2:sha256:260000$sqUWYLpaHFkWy9GT$38c37aa5be74d99c8db377cd31f2c12f7080372b2ed9e144b4671da5a72d9275','2023-02-24 12:56:37','2023-03-02 19:14:25');
INSERT INTO users VALUES(3,'David','pbkdf2:sha256:260000$Mo384fXjrWTQqVdk$27b0c1cb671743feaecc5a67575ede7fb5249988af6058520e11b0ed5fbd5e52','2023-02-26 22:31:51',NULL);
INSERT INTO users VALUES(4,'Alfred','pbkdf2:sha256:260000$za92QRdq9tV3uWZj$45d60c9dc455d01643d6cc95bf29826380b52b5f7dcf2ef2c2421437b2f9af0c','2023-02-27 12:45:31',NULL);
INSERT INTO users VALUES(5,'Annika','pbkdf2:sha256:260000$I4ap5fntmX6NUkwu$75bba8891895c6e238fcf734e4c4bd3cbee8fffbbbaf8ac76fb9eb2ac8c9a8d8','2023-02-27 19:04:01','2023-02-27 19:09:06');
INSERT INTO users VALUES(8,'Hansi','pbkdf2:sha256:260000$FBG61tX9Vwptvtlw$203dfc070c16423b5e7bb92aa49727388bff99d4683e304588146e0cb9ff769e','2023-03-01 16:20:03',NULL);
CREATE TABLE blog (
post_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
text TEXT NOT NULL,
title TEXT NOT NULL,
timestamp TEXT
);
INSERT INTO blog VALUES(2,'I just finished my blog, along with my personal admin-section of the website. As you can see, everything is working our great! I want to post my progress here for everyone to follow, who is interested! 😁','So it begins!','2023-02-24 13:28:46');
INSERT INTO blog VALUES(7,replace(replace('A lot has been done.\r\nI did a total rework of the optics. Bootstrap is nice to bring up a website very quick, but for a little more then basic styling, you are forced to write your own CSS. Some little animations really make a big difference.\r\nI currently still miss the ''About me'' and ''Projects'' sections, which are the most important for a portfolio. I will now implement these :)','\r',char(13)),'\n',char(10)),'Update 🙂','2023-03-02 15:26:57');
INSERT INTO blog VALUES(8,'This is a test blog-post for CS50','Hi','2023-03-02 18:29:43');
INSERT INTO blog VALUES(9,'This is a test entry for CS50 showcase','HI','2023-03-02 19:10:16');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('comments',34);
INSERT INTO sqlite_sequence VALUES('users',10);
INSERT INTO sqlite_sequence VALUES('blog',9);
COMMIT;
