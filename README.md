# MegaRAID Check

![GitHub Action CI badge](https://github.com/huntdatacenter/charm-megaraid-check/workflows/ci/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This subordinate charm is used to monitor MegaRAID controllers via NRPE (Nagios Remote Plugin Executor) with the [check_lsi_raid](https://github.com/thomas-krenn/check_lsi_raid) Nagios plugin from [Thomas-Krenn](https://www.thomas-krenn.com/).
This charm installs the StorCLI tool (Storage Command Line Tool) which is used interact with the MegaRAID controller on the host.

## Usage

This charm can be deployed to any principal application, but requires that the [nrpe](https://jaas.ai/nrpe) charm is deployed and related to it.
Here is an example where `ubuntu` is the principal application:

```shell
juju deploy cs:~huntdatacenter/megaraid-check
juju deploy nrpe
juju deploy ubuntu
juju deploy nagios
juju add-relation nrpe ubuntu
juju add-relation nrpe megaraid-check
juju add-relation ubuntu megaraid-check
juju add-relation nagios nrpe
```

## Further information

### Links

- [Thomas-Krenn GitHub repository for check_lsi_raid plugin](https://github.com/thomas-krenn/check_lsi_raid)
- [Thomas-Krenn wiki article for the check_lsi_raid plugin](https://www.thomas-krenn.com/en/wiki/LSI_RAID_Monitoring_Plugin)
- [Broadcom support documents and downloads for MegaRAID controllers](https://www.broadcom.com/support/download-search)
