#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM Matches;")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM Players;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT Count(*) FROM Players;")
    count = c.fetchone()[0]
    conn.close()
    return count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    sql = "INSERT INTO Players (Name) VALUES (%s);"
    data = (name,)
    c.execute(sql, data)
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        byes: the number of byes the player has played
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT Players.Id, Players.Name, SUM(CASE WHEN Matches.Winner=Players.Id THEN 1 ELSE 0 END) AS Wins, SUM(CASE WHEN Matches.Player1=Players.Id OR Matches.Player2=Players.Id THEN 1 ELSE 0 END) AS Matches, SUM(CASE WHEN (Matches.Player1=Players.Id OR Matches.Player2=Players.Id) AND (Matches.Player1 is NULL OR Matches.Player2 is NULL) THEN 1 ELSE 0 END) AS Byes From Players LEFT JOIN Matches on (Players.Id=Matches.Player1 OR Players.Id=Matches.Player2) GROUP BY Players.Id ORDER BY Wins DESC, Byes DESC;")
    result = c.fetchall()
    conn.close()
    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    # make sure a bye is never reported as a winner
    if winner == None:
        if loser == None: # both are None? Idiot...
            return
        winner = loser
        loser = 'NULL'

    conn = connect()
    c = conn.cursor()
    sql = "INSERT INTO Matches (Player1, Player2, Winner) VALUES (%s, %s, %s);"
    data = (winner, loser, winner,)
    c.execute(sql, data)
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    standings = playerStandings()

    # In general we will pair up alternate players based on their
    # place in the standings.
    even = standings[::2]
    odd = standings[1::2]

    # If there is an odd number of players we need to assign a bye.
    if (len(even) > len(odd)):

        # NOTE: although the spec says no one can have more than one bye,
        # what it means in a robust sense is that no player may have more
        # than one bye more than the minimum number of byes any player has.
        byeOffset = 4
        maxByes = 1 + min(map(lambda x: x[byeOffset], standings))

        # NOTE: playerStandings() sorts byes to the top of their win group
        # (ie: wins is primary sort key, byes is the secondary), so we will
        # bubble up the new bye from the bottom. There will never be more
        # than one bye per round.
        for i in xrange(len(standings)-1, 0, -1):
            player = standings[i]
            if player[byeOffset] < maxByes:
                # move the player who gets the bye to the end of the list
                # and stop searching.
                standings = standings[:i] + standings[i+1:] + [player]
                break

        # Construct a bye player (with an Id of None) and add it to
        # the end of the list, so it will be matched with the last
        # player in the list.
        byePlayer = (None, '', 0, 0, 0)
        standings = standings + [byePlayer]

        # reconstruct the even and odd lists for the pairings
        even = standings[::2]
        odd = standings[1::2]

    result = [p1+p2 for (p1,p2) in zip([(i[0],i[1]) for i in even], [(i[0],i[1]) for i in odd])]
    return result
