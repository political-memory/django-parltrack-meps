Introduction
============

Member of the parliament importation (from [parltrack](https://parltrack.euwiki.org)) and models extracted from [memopol](https://memopol.lqdn.fr) [code base](https://gitorious.org/memopol2-0).

In other words, this is the data of all the Member of the European Parliament: contact informations, committees, deleguations, groups, etc...

Usage
=====

Run:

    python manage.py update_meps

To import the last data on the MEPs.

Data Schema
===========

You can find a visualisation [here](https://raw.github.com/Psycojoker/django-parltrack-meps/master/graph.png).
Logic is pretty simple: MEP (Member of the European Parliament) at the center
and many2many with every instance.

Licence
=======

Like memopol: aGPLv3+
