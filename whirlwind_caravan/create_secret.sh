#!/bin/bash

user=$1
pass=$2

[ -z "$user" ] && read -p 'mongo username: ' user
[ -z "$pass" ] && read -p 'mongo password: ' pass

cat <<EOF
{
  "kind": "Secret",
  "apiVersion": "v1",
  "metadata": {
    "name": "mongo-secret"
  },
  "data": {
    "username": "$(echo $user | base64)",
    "password": "$(echo $pass | base64)"
  }
}
EOF
