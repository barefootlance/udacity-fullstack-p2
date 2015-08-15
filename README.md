# udacity-fullstack-p2
Udacity fullstack project #2: Tournament Results

This is an implementation of the specification for Tournament Results, the second project of the Udacity Full Stack Web Developer Nanodegree.

In addition to the basic functionality, this implements support for having an odd number of players in a tournament by implementing byes. Players are limited to having at most one bye more than the player who has the fewest byes. In a properly run Swiss tournament this effectively means that no one will have more than one bye, however if there are sufficient rounds (> N rounds for N players) it is guaranteed that no one has more than one bye more than anyone else.

Also implements a Standings view rather than creating it in code.

## Running the project

* Clone the repo: `git clone https://github.com/barefootlance/udacity-fullstack-p2.git`.
* Install Vagrant
* Install Virtual Box.
* cd into the fullstack-nanodegree-vm/vagrant folder, start up the virtual machine (vagrant up), move to the virtual command line (vagrant ssh).
* cd into /vagrant/tournament
* Run `psql`, then in the interpreter `\i tournament.sql` to initialize the PostgreSQL database on the virtual machine. `\q exits the interpreter.`
* Run `python tournament_test.py`

Running this file executes a small test suite to validate the python code.
