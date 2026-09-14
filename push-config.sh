#! /bin/bash
# Copies config/ to the printer, restarting Klipper only if something changed.
set -e

cd "$( dirname -- "${BASH_SOURCE[0]}" )"
if [ -f .env ]; then . ./.env; fi

./ansible.sh -e RPI_IP="${RPI_IP:?not set - copy .env.example to .env}" playbooks/config.yaml "$@"
