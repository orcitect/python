from fabric.api import *

import logging
logging.basicConfig(level=logging.ERROR)

env.forward_agent = True
env.use_ssh_config = True
env.ssh_config_path = "/home/oscar/.ssh/config"
env.timeout = 60
env.sudo_password = "Lada88kulaLada88kula"
env.gateway = 'admoscpet@cha-ba'



def block80():
    sudo('iptables -A INPUT -i eth0 -p tcp -m tcp --dport 80 -j DROP')

def open80():
    sudo('iptables -D INPUT -i eth0 -p tcp -m tcp --dport 80 -j DROP')

def upgrade_static():
    sudo('puppet agent --test --tags scs_apache_1_0_5;rpm -qa | grep casino-factory')

def upgrade_gee():
    sudo('puppet agent --test --tags gee_jboss_1_1_5;rpm -qa | grep casino-factory')

def jboss_stop():
    sudo('service jbossas stop')

def jboss_status():
    sudo('service jbossas status')

def jboss_start():
    sudo('service jbossas start')

def clear_log():
    sudo('rm -rf /var/lib/jbossas/standalone/{data,tmp}')

def uname():
    sudo('uname -r')

def puppet_test():
    sudo('puppet agent --test --noop')

def puppet_run():
    sudo('puppet agent --test')

def cert_backup():
    sudo('cp /etc/pki/java/cacerts{,.bak}')

def cert_import():
    sudo('keytool -import -alias SUBCA-1 -file subca-1.csmodule.com.crt -keystore /etc/pki/java/cacerts -storepass changeit')

def cert_delete():
    sudo('keytool -delete -alias SUBCA-1 -keystore /etc/pki/java/cacerts -storepass changeit')

def update_custom():
    sudo('puppet agent --test --tags globalcontentmanager_static_1_0_2;rpm -qa | grep lc-custom')

def yum_clean():
    sudo('yum clean all')

def ext_html():
    sudo('cd /tmp/;bash exthtmlscript.sh')