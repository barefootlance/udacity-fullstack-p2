-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create the tournament db and connect to it
CREATE DATABASE tournament;
\c tournament;

-- Create the Players table
CREATE TABLE Players (
  Id SERIAL PRIMARY KEY,
  Name varchar(255) NOT NULL
);

-- Create the Matches table
CREATE TABLE Matches (
  Id SERIAL PRIMARY KEY,
  Player1 int NOT NULL,
  Player2 int NOT NULL,
  Winner int
);