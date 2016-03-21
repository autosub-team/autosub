#!/bin/bash
set -e

if test $# -ne 1;
then
    echo "+++ Usage: build_deb.sh <version>"
    exit 1
fi

PACKAGE_NAME=autosub-$1
ORIG_PATH=$(pwd)

export EMAIL="andi.platschek@gmail.com"
export DEBFULLNAME="Andreas Platschek"

mkdir -p /tmp/$PACKAGE_NAME/bin
mkdir /tmp/$PACKAGE_NAME/doc
cd /tmp/$PACKAGE_NAME

git clone https://github.com/andipla/autosub.git

dh_make -y -i --native -c gpl2
dh_link /usr/share/pyshared/autosub/autosub.sh /usr/bin/autosub

#copy prepared config files
cp $ORIG_PATH/debian/control debian/
cp $ORIG_PATH/debian/autosub.install debian/
cp $ORIG_PATH/debian/rules debian/

dpkg-buildpackage -uc -us


#clean it all up
cd ..
cp autosub_${1}_all.deb $ORIG_PATH
cp autosub_${1}.tar.xz $ORIG_PATH

cd $ORIG_PATH
rm -rf /tmp/autosub-$1
