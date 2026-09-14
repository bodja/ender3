#! /bin/bash

SCRIPT_DIR=$( dirname -- "${BASH_SOURCE[0]}" )
cd ${SCRIPT_DIR}

printf 'Raspberry Pi IP: '
read answer

python3 -m venv "${SCRIPT_DIR}/.venv" && \
  source ${SCRIPT_DIR}/.venv/bin/activate && \
  pip install ansible==11.3.0 && \
  ansible-playbook -e rpi_ip="${answer}" -i ${SCRIPT_DIR}/inventory.yaml "${SCRIPT_DIR}/playbook.yaml"
