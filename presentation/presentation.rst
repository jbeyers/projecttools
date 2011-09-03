Plone meeting 7 Aug 2011
========================

A quick rundown of Fabric, a python tool for simple deploys.
------------------------------------------------------------

    * This is not pretty. So sue me.
    * All code: https://github.com/jbeyers/projecttools
        * This includes the presentation in rst format

Scenario
========

Assumptions:

    * Developers have ssh access and sudo rights under their own name.
    * Separate plone user with homedir.
    * Separate configurations:
        * dev.cfg
        * qa.cfg
        * production.cfg
    * Project in Git
    * Projects already built and running.
    * QA only started up as needed.

Buildout
========

Newest version of Fabric:
-------------------------

Use this fabric.cfg or add to dev.cfg::

    # fabric.cfg

    [buildout]
    parts =
        fabric

    [fabric]
    recipe= zc.recipe.egg

Note:

    * sudo apt-get install fabric also works, but you get an older version.
    * Rather install via buildout
    * Interactive prompt is available (Not so in older versions)

Command-line usage
==================

./bin/fab [commands]

    * Uses Paramiko python ssh library
    * Looks for fabfile.py in the current directory
    * Normal python script with functions
    * Each public function maps to a command
    * Commands can be chained:
        * ./bin/fab qa restart
        * ./bin/fab qa stop pull buildout start
        * ./bin/fab qa pull restart production status
    * env dictionary (More about that in a minute)

Command-line usage
==================

./bin/fab -l::

    Fabric script for deploying Plone consistently.

    Available commands:

        buildout    Rerun buildout.
        extra       Should normally just contain 'pass'. Useful for testing indi...
        production  Settings for the production server.
        pull        Do a git pull.
        qa          Settings for the qa server.
        restart     Restart just the zope instance, not the zeo.
        start       Start up the instance and zeo.
        status      Find out the running status of the server and deploy.
        stop        Shutdown the instance and zeo.
        update      Update code on the server and restart zope.


Command-line usage
==================

./bin/fab qa update::

    [gogo.clouditto.com] Executing task 'update'
    [gogo.clouditto.com] sudo: git pull
    [gogo.clouditto.com] out: sudo password: 
    [gogo.clouditto.com] out: 
    [gogo.clouditto.com] out: Enter passphrase for key '/home/plone/.ssh/id_rsa': 
    [gogo.clouditto.com] out: remote: Counting objects: 5, done.
    [gogo.clouditto.com] out: remote: Compressing objects: 100% (3/3), done.
    [gogo.clouditto.com] out: remote: Total 3 (delta 2), reused 0 (delta 0)
    [gogo.clouditto.com] out: Unpacking objects: 100% (3/3), done.
    [gogo.clouditto.com] out: From git.assembla.com:simmonds_portal
    [gogo.clouditto.com] out:    66ab408..57e222d  master     -> origin/master
    [gogo.clouditto.com] out: Updating 66ab408..57e222d
    [gogo.clouditto.com] out: Fast-forward
    [gogo.clouditto.com] out:  fabfile.py |    5 ++++-
    [gogo.clouditto.com] out:  1 files changed, 4 insertions(+), 1 deletions(-)
    [gogo.clouditto.com] out: 
    [gogo.clouditto.com] sudo: ./bin/instance restart
    [gogo.clouditto.com] out: . . . . . . . . . . . 
    [gogo.clouditto.com] out: daemon process restarted, pid=28387
    [gogo.clouditto.com] out: 

    Done.
    Disconnecting from gogo.clouditto.com... done.

Basic imports
=============

.. code-block:: python

    # fabfile.py

    """
    Fabric script for deploying Plone consistently.
    """

    from __future__ import with_statement
    from fabric.api import env, cd, sudo, run

    try:
        from fab_config import *
    except:
        pass

Note:
-----

    * with cd, local, run, sudo
    * Try to import fab_config
    * fab_config.py used for site-specific settings in env

Typical fab_config.py
=====================

.. code-block:: python

    # fab_config.py

    from fabric.api import env

    def qa():
        """
        Settings for the qa server.
        """
        env.buildout_config = 'qa'
        env.hosts = ['myqaserver.mysite.com']
        env.deploy_user = 'plone'
        env.directory = '/home/%s/instances/qa.mysite' % env.deploy_user

env dictionary
--------------

    * Global
    * Like bash environment variables
    * Add anything
    * hosts is special (but not for now)

Stop and start
==============

.. code-block:: python

    def stop():
        """
        Shutdown the instance and zeo.
        """
        with cd(env.directory):
            sudo('./bin/instance stop', user=env.deploy_user)
            sudo('./bin/zeoserver stop', user=env.deploy_user)
            
    def start():
        """
        Start up the instance and zeo.
        """
        with cd(env.directory):
            sudo('./bin/zeoserver start', user=env.deploy_user)
            sudo('./bin/instance start', user=env.deploy_user)

Note:

    * with cd changes into a directory for the in-scope commands
    * sudo either to root (no user specified) or the given user.

Git pull and restart
====================

.. code-block:: python

    def pull():
        """
        Do a git pull.
        """
        with cd(env.directory):
            sudo('git pull', user=env.deploy_user)


    def restart():
        """
        Restart just the zope instance, not the zeo.
        """
        with cd(env.directory):
            sudo('./bin/instance restart', user=env.deploy_user)

Git pull and restart combined
=============================

.. code-block:: python

    def update():
        """
        Update code on the server and restart zope.
        """
        pull()
        restart()

Server health and status
========================

.. code-block:: python

    def status():
        """
        Find out the running status of the server and deploy.
        """

        # General health of the server.
        run('uptime')
        run('free')
        run('df -h')

        # Deploy and running status
        with cd(env.directory):
            sudo('./bin/instance status', user=env.deploy_user)
            sudo('git status', user=env.deploy_user)
            sudo('git log -1', user=env.deploy_user)
        
The rest
========

Do a buildout with correct config file:

.. code-block:: python

    def buildout():
        """
        Rerun buildout.
        """
        with cd(env.directory):
            sudo('./bin/buildout -Nvc %s.cfg' % env.buildout_config,
                 user=env.deploy_user)

Useful bit of scaffolding:

.. code-block:: python

    def extra():
        """
        Should normally just contain 'pass'. Useful for testing individual
        commands before integrating them into another function.
        """
        pass

Future
======

Some future enhancements:
    * get and put files from/to the server. How about:
        * Timestamped versions of Data.fs automatically zipped
        * Copied to the dev instance
    * Do the initial buildout too
    * Or make sure all the needed packages are installed
    * Refactor methods for deploy user:
        * All are with cd (env.directory)
        * All are as the deploy user.
        * Single method that takes a list of command strings.
        * (Already done)

Links
=====

    * Fabric: http://fabfile.org
    * code: https://github.com/jbeyers/projecttools
    * rst2pdf for presentations: http://lateral.netmanagers.com.ar/stories/BBS52.html
