"""
Fabric settings for hosts.
"""

from fabric.api import env

def qa():
    """
    Settings for the qa server.
    """

    # If your buildout file for QA is qa.cfg, the following line is correct:
    #env.buildout_config = 'qa'

    # A list of hostnames to deploy on. The following will try to connect to
    # myqaserver.mysite.com as your username:
    #env.hosts = ['myqaserver.mysite.com']

    # The deploy user. Most deploy commands will be run as this user.
    #env.deploy_user = 'plone'

    # The root of your Plone instance. By convention, I put the plone instances
    # in an 'instances' directory in the deploy users home directory.
    #env.directory = '/home/%s/instances/qa.mysite' % env.deploy_user
