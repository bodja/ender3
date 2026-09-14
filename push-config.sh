#! /bin/bash
# Copies config/ to the printer, restarting Klipper only if something changed.
set -e

printf 'Raspberry Pi IP: '
read RPI_IP

"$( dirname -- "${BASH_SOURCE[0]}" )/ansible.sh" \
  -e rpi_ip="${RPI_IP}" playbooks/config.yaml "$@"
