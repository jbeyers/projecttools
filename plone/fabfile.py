"""
Fabric script for deploying Plone consistently.
"""

from __future__ import with_statement
from fabric.api import env, cd, sudo, run

try:
    from fab_config import *
except:
    pass

def pull():
    """
    Do a git pull.
    """
    with cd(env.directory):
        sudo('git pull', user=env.deploy_user)

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

def restart():
    """
    Restart just the zope instance, not the zeo.
    """
    with cd(env.directory):
        sudo('./bin/instance restart', user=env.deploy_user)

def status():
    """
    Find out the running status of the server and deploy.
    """

    # General health of the server.
    run('uptime')
    # On an 80-column terminal, uptime cuts off the load averages, so get them.
    run('free')
    run('df -h')

    # Deploy and running status
    with cd(env.directory):
        sudo('./bin/instance status', user=env.deploy_user)
        sudo('git status', user=env.deploy_user)
        sudo('git log -1', user=env.deploy_user)
    
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
    with cd(env.directory):
        sudo('./bin/buildout -Nvc %s.cfg' % env.buildout_config,
             user=env.deploy_user)

def extra():
    """
    Should normally just contain 'pass'. Useful for testing individual commands before integrating them into another function.
    """
    pass
