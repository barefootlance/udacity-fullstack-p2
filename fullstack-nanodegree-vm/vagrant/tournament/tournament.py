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
    sqlCud("DELETE FROM Matches;")


def deletePlayers():
    """Remove all the player records from the database."""
    sqlCud("DELETE FROM Players;")


def countPlayers():
    """Returns the number of players currently registered."""
    return sqlReadScalar("SELECT Count(*) FROM Players;")


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    sqlCud("INSERT INTO Players (Name) VALUES (%s);", (name,))


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
    return sqlRead("SELECT * FROM Standings")


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
        loser = None

    sqlCud(
        "INSERT INTO Matches (Winner, Loser) VALUES (%s, %s);",
        (winner, loser))


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Each player appears exactly once in the pairings.  Each player is paired
    with another player with an equal or nearly-equal win record, that is, a
    player adjacent to him or her in the standings.

    If there are an odd number of players one player will get a bye, that
    is the player will be matched with an opponent with an id of None.
    A player will not receive a bye if they already have more byes than
    any other player in the tournament. The bye will go to the player
    lowest in the standings who does not already have too many byes.

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

def sqlCud(sql, data=()):
    """ Executes a sql command and commits the changes"""
    return sqlExecute(sql, data)

def sqlReadScalar(sql, data=()):
    """ Executes a sql query.

    Returns:
        A scalar value from the query.
    """
    return sqlExecute(sql, data, 'fetchone')[0]

def sqlRead(sql, data=()):
    """ Executes a sql query.

    Returns:
        A scalar value from the query.
    """
    return sqlExecute(sql, data, 'fetchall')

def sqlExecute(sql, data, resultMethodName=None):
    """ Generic sql execution.

    Returns:
        if resultMethod is provided, returns the result of that method.
        Examples would be 'fetchall' or 'fetchone'
    """
    conn = connect()
    c = conn.cursor()
    c.execute(sql, data)
    if resultMethodName == None:
        conn.commit()
        conn.close()
    else:
        result = getattr(c, resultMethodName)()
        conn.close()
        return result
