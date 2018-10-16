#!/bin/bash

TEST_DIR=scripts/tests
REDIS_VERSION=4.0.11
REDIS_NAME=redis
REDIS_NAME_AND_VERSION=redis-${REDIS_VERSION}
REDIS_BIN_DIR=${TEST_DIR}/${REDIS_NAME}/bin
REDIS_ARCHIVE=${REDIS_NAME_AND_VERSION}.tar.gz
REDIS_SRC_BIN=${TEST_DIR}/${REDIS_NAME_AND_VERSION}/src

pip install -r ${TEST_DIR}/test_requirements.txt

if [ ! -d ${REDIS_BIN_DIR} ]; then
    echo "Generating binaries for the test redis server"
    cd ${TEST_DIR}
    tar xzf ${REDIS_ARCHIVE}
    cd ${REDIS_NAME_AND_VERSION}
    make
    cd .. && cd .. && cd ..
    mkdir ${REDIS_BIN_DIR}
    cp -R ${REDIS_SRC_BIN}/** ${REDIS_BIN_DIR}
    rm -R ${TEST_DIR}/${REDIS_NAME_AND_VERSION}
fi