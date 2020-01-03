#!/usr/bin/env python

from charmhelpers.contrib.ansible import apply_playbook
from charmhelpers.contrib.charmsupport import nrpe
from charmhelpers.core.hookenv import application_version_set
from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import hook_name
from charmhelpers.core.hookenv import log
from charmhelpers.core.hookenv import status_set
from charms.layer.nagios import install_nagios_plugin_from_file
from charms.reactive.decorators import hook
from charms.reactive.decorators import when
from charms.reactive.decorators import when_not
from charms.reactive.flags import clear_flag
from charms.reactive.flags import register_trigger
from charms.reactive.flags import set_flag

PLUGIN_NAME = 'check_lsi_raid'

register_trigger(when='config.changed.check_parameters',
                 clear_flag='megaraid.configured')
register_trigger(when='config.changed.check_repo',
                 clear_flag='megaraid.installed')
register_trigger(when='config.changed.check_version',
                 clear_flag='megaraid.installed')
register_trigger(when='config.changed.storcli_path',
                 clear_flag=['megaraid.installed', 'megaraid.configured'])
register_trigger(when='config.changed.storcli_url',
                 clear_flag='megaraid.installed')


@when_not('megaraid.version')
def set_version():
    try:
        with open(file='repo-info') as f:
            for line in f:
                if line.startswith('commit-short'):
                    commit_short = line.split(':')[-1].strip()
                    application_version_set(commit_short)
    except IOError:
        log('Cannot set application version. Missing repo-info file.')
    set_flag('megaraid.version')


@when_not('nrpe-external-master.available')
def missing_nrpe():
    if hook_name() == 'update-status':
        status_set('waiting', 'waiting on relation to nrpe')
    else:
        status_set('blocked', 'missing relation to nrpe')


@when('nrpe-external-master.available')
@when_not('megaraid.installed')
def install_megaraid():
    status_set('maintenance', 'installing megaraid check')
    apply_playbook(playbook='ansible/playbook.yaml',
                   extra_vars=dict(plugin_name=PLUGIN_NAME))
    set_flag('megaraid.installed')


@when('megaraid.installed')
@when('nrpe-external-master.available')
@when_not('megaraid.configured')
def configure_megaraid():
    status_set('maintenance', 'configuring megaraid check')
    install_nagios_plugin_from_file(
        source_file_path='/opt/{}/{}'.format(PLUGIN_NAME, PLUGIN_NAME),
        plugin_name=PLUGIN_NAME
    )
    hostname = nrpe.get_nagios_hostname()
    nrpe_setup = nrpe.NRPE(hostname=hostname, primary=False)
    nrpe_setup.add_check(
        shortname=PLUGIN_NAME,
        description=PLUGIN_NAME,
        check_cmd='{plugin_name} -p {storcli_path} {check_params}'.format(
            plugin_name=PLUGIN_NAME,
            storcli_path=config('storcli_path'),
            check_params=config('check_parameters'))
    )
    nrpe_setup.write()
    status_set('active', 'ready')
    set_flag('megaraid.configured')


# Hooks
@hook('upgrade-charm')
def upgrade_charm():
    clear_flag('megaraid.version')
    clear_flag('megaraid.configured')
