#! /bin/bash
set -e

printf 'Raspberry Pi IP: '
read RPI_IP

"$( dirname -- "${BASH_SOURCE[0]}" )/ansible.sh" \
  -e rpi_ip="${RPI_IP}" playbook.yaml "$@"
