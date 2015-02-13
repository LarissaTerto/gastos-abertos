# -*- coding: utf-8 -*-

# http://docs.fabfile.org/en/1.5/tutorial.html

from fabric.api import *
from fabric.network import ssh
from flask.ext.script import Manager

from gastosabertos.extensions import db
from gastosabertos import create_app

app = create_app()

project = "gastosabertos"

env.user = 'gastosabertos'
env.hosts = ['gastosabertos.org']
#env.key_filename = '~/.ssh/ga_id_rsa'


def reset():
    """
    Reset local debug env.
    """

    local("rm -rf /tmp/instance")
    local("mkdir /tmp/instance")


def setup():
    """
    Setup virtual env.
    """

    local("virtualenv env")
    activate_this = "env/bin/activate_this.py"
    execfile(activate_this, dict(__file__=activate_this))
    local("python setup.py install")
    reset()


def deploy():
    """
    Deploy project to Gastos Abertos server
    """

    project_dir = '/home/gastosabertos/gastos_abertos'
    with cd(project_dir):
        run("git pull")
        with prefix("source /home/gastosabertos/.virtualenvs/ga/bin/activate"):
            run("python setup.py install")
        run("touch wsgi.py")


def initdb():
    """
    Init or reset database
    """

    with app.app_context():
        db.drop_all()
        db.create_all()


def importdata(place="local", lines_per_insert=100):
    """
    Import data to the local DB
    """

    import_commands = """
    python utils/import_revenue_codes.py
    python utils/import_revenue.py data/receitas_min.csv {lines_per_insert}
    """.format(lines_per_insert=lines_per_insert)

    if place == "remote":
        run(import_commands)
    elif place == "local":
        local(import_commands)
    else:
        print("Where to import? 'local' or 'remote'?")


def d():
    """
    Debug.
    """

    reset()
    local("python manage.py run")


def babel():
    """
    Babel compile.
    """

    local("python setup.py compile_catalog --directory `find -name translations` --locale zh -f")
