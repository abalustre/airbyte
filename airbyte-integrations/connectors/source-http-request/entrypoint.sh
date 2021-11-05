#!/bin/sh

set_ssl="false"
for i in "$@"; do
    if [ "$i" = "read" ] || [ "$i" = "discover" ]; then
        set_ssl="true"
    fi
done

if [ "$set_ssl" = "true" ]; then
    cmd="check ${2} ${3}"
    python /airbyte/integration_code/main.py $cmd
fi

python /airbyte/integration_code/main.py $@
