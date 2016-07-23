from fabric.api import local
from fabric.api import lcd

def prepare_deployment(branch_name):
    local('python manage.py test')
    local('git checkout master && git merge ' + branch_name)

def deploy():
    with lcd('interpopulus@interpopulus.webfactional.com:/home/interpopulus/webapps/acressity/acressity'):
        local('git pull /home/asgaines/Documents/Code/Websites/acressity')
        local('python manage.py makemigrations')
        local('python manage.py migrate')
        local('python manage.py test')
