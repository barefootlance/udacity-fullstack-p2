-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create the tournament db and connect to it
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

-- Create the Players table
DROP TABLE IF EXISTS Players;
CREATE TABLE Players (
  Id SERIAL PRIMARY KEY,
  Name varchar(255) NOT NULL
);

-- Create the Matches table
DROP TABLE IF EXISTS Matches;
CREATE TABLE Matches (
  Id SERIAL PRIMARY KEY,
  Player1 int REFERENCES Players(Id),
  Player2 int REFERENCES Players(Id),
  Winner int REFERENCES Players(Id)
);

-- Create a view for the player standings
CREATE OR REPLACE VIEW Standings AS
  SELECT Players.Id,
         Players.Name,
         SUM(CASE WHEN Matches.Winner=Players.Id THEN 1 ELSE 0 END) AS Wins,
         SUM(CASE WHEN Matches.Player1=Players.Id OR Matches.Player2=Players.Id THEN 1 ELSE 0 END) AS Matches,
         SUM(CASE WHEN (Matches.Player1=Players.Id AND Matches.Player2 is NULL) OR (Matches.Player1 is NULL AND Matches.Player2=Players.Id) THEN 1 ELSE 0 END) AS Byes
  From Players
  LEFT JOIN Matches on (Players.Id=Matches.Player1 OR Players.Id=Matches.Player2)
  GROUP BY Players.Id
  ORDER BY Wins DESC, Byes DESC;
