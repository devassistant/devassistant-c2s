#!/usr/bin/bash

for pkg in client server; do
    pushd $pkg

    # Clean Python tarballs
    rm -rf dist
    rm docker/*.gz

    ./setup.py sdist
    cp dist/*.gz docker

    cd docker
    sudo docker build -t da-$pkg .
    popd

done

