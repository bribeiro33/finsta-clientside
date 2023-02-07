PRAGMA foreign_keys = ON;

--SELECT * FROM users--
INSERT INTO users(username, fullname, email, filename, password)
VALUES ('awdeorio', 'Andrew DeOrio', 'awdeorio@umich.edu', 'e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO users(username, fullname, email, filename, password)
VALUES ('jflinn', 'Jason Flinn', 'jflinn@umich.edu', '505083b8b56c97429a728b68f31b0b2a089e5113.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO users(username, fullname, email, filename, password)
VALUES ('michjc', 'Michael Cafarella', 'michjc@umich.edu', '5ecde7677b83304132cb2871516ea50032ff7a4f.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO users(username, fullname, email, filename, password)
VALUES ('jag', 'H.V. Jagadish', 'jag@umich.edu', '73ab33bd357c3fd42292487b825880958c595655.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

--SELECT * FROM posts--
INSERT INTO posts(postid, filename, owner)
VALUES ('1', '122a7d27ca1d7420a1072f695d9290fad4501a41.jpg', 'awdeorio');

INSERT INTO posts(postid, filename, owner)
VALUES ('2', 'ad7790405c539894d25ab8dcf0b79eed3341e109.jpg', 'jflinn');

INSERT INTO posts(postid, filename, owner)
VALUES ('3', '9887e06812ef434d291e4936417d125cd594b38a.jpg', 'awdeorio');

INSERT INTO posts(postid, filename, owner)
VALUES ('4', '2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg', 'jag');

--SELECT * FROM following--
INSERT INTO following(username1, username2)
VALUES ('awdeorio', 'jflinn');

INSERT INTO following(username1, username2)
VALUES ('awdeorio', 'michjc');

INSERT INTO following(username1, username2)
VALUES ('jflinn', 'awdeorio');

INSERT INTO following(username1, username2)
VALUES ('jflinn', 'michjc');

INSERT INTO following(username1, username2)
VALUES ('michjc', 'awdeorio');

INSERT INTO following(username1, username2)
VALUES ('michjc', 'jag');

INSERT INTO following(username1, username2)
VALUES ('jag', 'michjc');

--SELECT * FROM comments--
INSERT INTO comments(commentid, owner, postid, text)
VALUES ('1', 'awdeorio', '3', '#chickensofinstagram');

INSERT INTO comments(commentid, owner, postid, text)
VALUES ('2', 'jflinn', '3', 'I <3 chickens');

INSERT INTO comments(commentid, owner, postid, text)
VALUES ('3', 'michjc', '3', 'Cute overload!');

INSERT INTO comments(commentid, owner, postid, text)
VALUES ('4', 'awdeorio', '2', 'Sick #crossword');

INSERT INTO comments(commentid, owner, postid, text)
VALUES ('5', 'jflinn', '1', 'Walking the plank #chickensofinstagram');

INSERT INTO comments(commentid, owner, postid, text)
VALUES ('6', 'awdeorio', '1', 'This was after trying to teach them to do a #crossword');

INSERT INTO comments(commentid, owner, postid, text)
VALUES ('7', 'jag', '4', 'Saw this on the diag yesterday!');

--SELECT * FROM likes--
INSERT INTO likes(likeid, owner, postid)
VALUES ('1', 'awdeorio', '1');

INSERT INTO likes(likeid, owner, postid)
VALUES ('2','michjc', '1');

INSERT INTO likes(likeid, owner, postid)
VALUES ('3', 'jflinn', '1');

INSERT INTO likes(likeid, owner, postid)
VALUES ('4', 'awdeorio', '2');

INSERT INTO likes(likeid, owner, postid)
VALUES ('5', 'michjc', '2');

INSERT INTO likes(likeid, owner, postid)
VALUES ('6', 'awdeorio', '3');