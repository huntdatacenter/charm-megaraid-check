#!/usr/bin/env python

from charmhelpers.contrib.ansible import apply_playbook
from charmhelpers.contrib.charmsupport import nrpe
from charmhelpers.core.hookenv import application_version_set
from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import hook_name
from charmhelpers.core.hookenv import log
from charmhelpers.core.hookenv import status_set
from charms.reactive import hook
from charms.reactive import remove_state
from charms.reactive import set_state
from charms.reactive import when
from charms.reactive import when_any
from charms.reactive import when_not

CHECK_NAME = 'megaraid'
PLUGIN_NAME = 'check_lsi_raid'
STORCLI_PATH = '/opt/MegaRAID/storcli/storcli64'


@when_not('megaraid.version')
def set_version():
    try:
        with open(file='repo-info') as f:
            for line in f:
                if line.startswith('commit-short'):
                    commit_short = line.split(':')[-1].strip()
                    application_version_set(commit_short)
    except IOError:
        log('Cannot set application version. Missing repo-info.')
    set_state('megaraid.version')


@when('nrpe-external-master.available')
@when_not('megaraid.installed')
def install_deps():
    status_set('maintenance', 'installing dependencies')
    apply_playbook(
        playbook='ansible/playbook.yaml',
        extra_vars=dict(plugin_name=PLUGIN_NAME,
                        storcli_path=STORCLI_PATH))
    status_set('active', 'ready')
    set_state('megaraid.installed')


@when('megaraid.installed')
@when('nrpe-external-master.available')
@when_not('megaraid.configured')
def configure_check():
    status_set('maintenance', 'configuring {} check'.format(CHECK_NAME))
    check_params = config('check-parameters')
    hostname = nrpe.get_nagios_hostname()
    nrpe_setup = nrpe.NRPE(hostname=hostname, primary=False)
    nrpe_setup.add_check(
        shortname=CHECK_NAME,
        description=CHECK_NAME,
        check_cmd='{plugin_name} -p {storcli_path} {check_params}'.format(
            plugin_name=PLUGIN_NAME,
            storcli_path=STORCLI_PATH,
            check_params=check_params)
    )
    nrpe_setup.write()
    status_set('active', 'ready')
    set_state('megaraid.configured')


@when_not('nrpe-external-master.available')
def missing_nrpe():
    if hook_name() == 'update-status':
        status_set('maintenance', 'waiting on relation to nrpe')
    else:
        status_set('blocked', 'missing relation to nrpe')


@when('megaraid.configured')
@when_not('nrpe-external-master.available')
def lost_nrpe():
    remove_check()
    remove_state('megaraid.configured')


# Configs
@when('nrpe-external-master.available')
@when_any('config.changed.storcli-url',
          'config.changed.check-version',
          'config.changed.check-repo')
def deps_changed():
    remove_state('megaraid.installed')


@when('nrpe-external-master.available')
@when_any('config.changed.nagios_context',
          'config.changed.nagios_servicegroups',
          'config.changed.check-parameters')
def check_changed():
    remove_state('megaraid.configured')


@when('nrpe-external-master.available')
@when('config.changed.check-remove')
def remove_check_changed():
    if config('check-remove'):
        remove_check()
    else:
        configure_check()


# Hooks
@hook('stop')
def stop():
    remove_check()
    apply_playbook(
        playbook='ansible/playbook.yaml',
        tags=['uninstall'],
        extra_vars=dict(plugin_name=PLUGIN_NAME,
                        storcli_path=STORCLI_PATH))


@hook('upgrade-charm')
def upgrade_charm():
    remove_state('megaraid.version')
    remove_state('megaraid.installed')
    remove_state('megaraid.configured')


# Functions
def remove_check():
    nrpe_setup = nrpe.NRPE(primary=False)
    nrpe_setup.remove_check(shortname=CHECK_NAME)
    nrpe_setup.write()
