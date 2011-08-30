"""
Fabric script for deploying Plone consistently.
"""

from __future__ import with_statement
from fabric.api import env, cd, sudo, run

try:
    from fab_config import *
except:
    pass

def _with_deploy_env(commands=[]):
    """
    Run a set of commands as the deploy user in the deploy directory.
    """
    with cd(env.directory):
        for command in commands:
            sudo(command, user=env.deploy_user)

def pull():
    """
    Do a git pull.
    """
    _with_deploy_env(['git pull'])

def stop():
    """
    Shutdown the instance and zeo.
    """
    _with_deploy_env(['./bin/instance stop', './bin/zeoserver stop'])
        
def start():
    """
    Start up the instance and zeo.
    """
    _with_deploy_env(['./bin/zeoserver start', './bin/instance start'])

def restart():
    """
    Restart just the zope instance, not the zeo.
    """
    _with_deploy_env(['./bin/instance restart'])

def status():
    """
    Find out the running status of the server and deploy.
    """

    # General health of the server.
    run('cat /proc/loadavg')
    run('uptime')
    run('free')
    run('df -h')

    # Deploy and running status
    _with_deploy_env(['./bin/instance status', 'git status', 'git log -1'])
    
def update():
    """
    Update code on the server and restart zope.
    """
    pull()
    restart()

def buildout():
    """
    Rerun buildout.
    """
    _with_deploy_env(['./bin/buildout -Nvc %s.cfg' % env.buildout_config])

def extra():
    """
    Should normally just contain 'pass'. Useful for testing individual commands before integrating them into another function.
    """
    pass
