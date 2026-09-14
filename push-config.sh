#! /bin/bash
# Copies config/ to the printer, restarting Klipper only if something changed.
set -e

"$( dirname -- "${BASH_SOURCE[0]}" )/ansible.sh" playbooks/config.yaml "$@"
