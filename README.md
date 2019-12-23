# MegaRAID Check

![GitHub Action CI badge](https://github.com/huntdatacenter/charm-megaraid-check/workflows/ci/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This subordinate charm is used to monitor MegaRAID controllers via NRPE (Nagios Remote Plugin Executor) with the [check_lsi_raid](https://github.com/thomas-krenn/check_lsi_raid) Nagios plugin from [Thomas-Krenn](https://www.thomas-krenn.com/).
This charm installs the StorCLI tool (Storage Command Line Tool) which is used interact with the MegaRAID controller on the host.

## Usage

This charm can be deployed to any principal application, but requires that the [nrpe](https://jaas.ai/nrpe) charm is deployed and related to it.
Here is an example where `ubuntu` is the principal application:

```
juju deploy cs:~huntdatacenter/megaraid-check
juju deploy nrpe
juju deploy ubuntu
juju deploy nagios
juju add-relation nrpe ubuntu
juju add-relation nrpe megaraid-check
juju add-relation ubuntu megaraid-check
juju add-relation nagios nrpe
```

## Development

Here are some helpful commands to get started with development and testing:

```
$ make help
lint                 Run linter
build                Build charm
deploy               Deploy charm
upgrade              Upgrade charm
force-upgrade        Force upgrade charm
test-xenial-bundle   Test Xenial bundle
test-bionic-bundle   Test Bionic bundle
push                 Push charm to stable channel
clean                Clean .tox and build
help                 Show this help
```

## Further information

### Links

- [Thomas-Krenn GitHub repository for check_lsi_raid plugin](https://github.com/thomas-krenn/check_lsi_raid)
- [Thomas-Krenn wiki article for the check_lsi_raid plugin](https://www.thomas-krenn.com/en/wiki/LSI_RAID_Monitoring_Plugin)
- [Broadcom support documents and downloads for MegaRAID controllers](https://www.broadcom.com/support/download-search)
