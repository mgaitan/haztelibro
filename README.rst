haztelibro
==========

give a file with a list of urls, get a readable epub


Usage
------

Define your input file. Suppose you create ``darwin.txt`` with this content::

    http://anthro.palomar.edu/evolve/evolve_2.htm
    # this line is a comment
    http://en.wikipedia.org/wiki/Charles_Darwin
    http://www.theatlantic.com/technology/archive/2012/06/a-perfect-and-beautiful-machine-what-darwins-theory-of-evolution-reveals-about-artificial-intelligence/258829/

Then run::

    $ python main.py darwin.txt darwin-book


