CREATE SCHEMA development;
CREATE SCHEMA production;


CREATE TABLE development.queue_msg_hash (
	hashkey VARCHAR(64) PRIMARY KEY,
	queue_name VARCHAR(64),
    timestamp TIMESTAMP default NULL
);