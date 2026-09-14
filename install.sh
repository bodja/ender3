#! /bin/bash
set -e

"$( dirname -- "${BASH_SOURCE[0]}" )/ansible.sh" playbook.yaml "$@"
