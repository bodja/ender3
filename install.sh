#! /bin/bash
set -e

ANSIBLE_VERSION=14.4.0  # keep in sync with .pre-commit-config.yaml

SCRIPT_DIR=$( dirname -- "${BASH_SOURCE[0]}" )
cd ${SCRIPT_DIR}

if ! command -v uv > /dev/null; then
  echo 'uv not found: https://docs.astral.sh/uv/getting-started/installation/'
  exit 1
fi

printf 'Raspberry Pi IP: '
read answer

uv run --no-project --with "ansible==${ANSIBLE_VERSION}" \
  ansible-playbook -e rpi_ip="${answer}" -i inventory.yaml playbook.yaml
