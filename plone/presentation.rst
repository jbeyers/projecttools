Using Fabric for consistent deployment

Scenario:
    * 2 developers have access
    * Separate Plone user with homedir
    * Separate dev, qa, production builds
    * Project in GIT
    * Project already running
    * QA only started up as needed.

Buildout:
Newest version: Interactive prompt better
fabric.cfg or add to dev.cfg::

    [buildout]
    parts =
        fabric

    [fabric]
    recipe= zc.recipe.egg

Fabric basics:

./bin/fab [commands]
    * Paramiko for ssh
    * Looks for fabfile.py
    * Normal python script with functions
    * Each function maps to a command
    * Commands can be chained (./bin/fab qa stop pull buildout start)
    * env dictionary (More about that in a minute)

Typical outputs:

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

env dictionary:
    * Global
    * Like bash environment variables
    * Add anything
    * hosts is special (but not for now)

Basic imports:
    * with cd, local, run, sudo
    * Try to import fab_config
    * fab_config.py used for site-specific settings in env

What it looks like::

    from __future__ import with_statement
    from fabric.api import env, cd, sudo, run

    try:
        from fab_config import *
    except:
        pass

Typical fab_config.py::
    
    from fabric.api import env

    def qa():
        """
        Settings for the qa server.
        """
        env.buildout_config = 'qa'
        env.hosts = ['myqaserver.mysite.com']
        env.deploy_user = 'plone'
        env.directory = '/home/%s/instances/qa.mysite' % env.deploy_user

Stop and start::
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

Git pull and restart::

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

    def update():
        """
        Update code on the server and restart zope.
        """
        pull()
        restart()

Server health and status::

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
        
Do a buildout with correct config file::

    def buildout():
        """
        Rerun buildout.
        """
        with cd(env.directory):
            sudo('./bin/buildout -Nvc %s.cfg' % env.buildout_config,
                 user=env.deploy_user)

Useful bit of scaffolding::

    def extra():
        """
        Should normally just contain 'pass'. Useful for testing individual commands before integrating them into another function.
        """
        pass

