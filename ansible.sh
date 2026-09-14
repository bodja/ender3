#! /bin/bash
# Runs ansible-playbook against this repo's inventory, with the version it pins.
set -e

ANSIBLE_VERSION=14.4.0

cd "$( dirname -- "${BASH_SOURCE[0]}" )"

if ! command -v uv > /dev/null; then
  echo 'uv not found: https://docs.astral.sh/uv/getting-started/installation/'
  exit 1
fi

exec uv run --no-project --with "ansible==${ANSIBLE_VERSION}" \
  ansible-playbook -i inventory.yaml "$@"
