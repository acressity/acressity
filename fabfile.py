from fabric.api import local
from fabric.api import cd, run

def prepare_deployment(branch_name):
    local('python manage.py test')
    local('git checkout master && git merge ' + branch_name)
    local('git push origin')

def deploy():
    with cd('/home/interpopulus/webapps/acressity/acressity'):
        #run('git fetch origin')
        #run('python manage.py makemigrations')
        run('python manage.py migrate')
        #run('./manage.py test')
        #run('./webapps/acressity/apache/bin/restart')
