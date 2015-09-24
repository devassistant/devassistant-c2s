#!/usr/bin/bash

if $(test -z $DEV_UID); then
    DEV_UID=1000
fi

if $(test -z $DEV_GID); then
    DEV_GID=$DEV_UID
fi

groupadd dev -g $DEV_GID
useradd dev -u $DEV_UID -g $DEV_GID

sudo -u dev python3.4 da-server $*
