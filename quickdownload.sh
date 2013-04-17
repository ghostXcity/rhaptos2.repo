# Copyright (c) 2013 Rice University
#
# This software is subject to the provisions of the GNU AFFERO GENERAL PUBLIC LICENSE Version 3.0 (AGPL).
# See LICENSE.txt for details.

set -e

### USAGE
USAGE="bash foo.sh TGTDIR"
## setup as simply but non-destructively teh Rhaptos2 repo
## assumes we are on POSIX and have curl

### We have a script to build a Venv - buildvenv.sh
### This makes no assumptions about hard coded URLS or paths.
### However to be actually user friendly we *do* have to make such assumptions
### so ...

### This script will assume it is in an empty directory and that


function isempty() {
    ###if anything other than$1 is empty exit
    dir=$1

    [ $# -eq 0 ] && { echo "Usage: $USAGE"; exit 2; }
    [ ! -d "$dir" ] && { echo "$dir is not a directory."; exit 2; }

    if find "$dir" -maxdepth 0 -empty | read;
    then
     echo "$dir empty."
    else
     echo "$dir not empty. Please supply an empty target dir."; exit 2;
    fi
}

function download_src(){

    ### This is fantastically brittle but needs to exist to make the
    ### overall easy-to-install process work

    mkdir -p -m 0755 $SRC
    mkdir -p -m 0755 $VENVS
    cd $SRC
    git clone https://github.com/Connexions/rhaptos2.repo.git
    git clone https://github.com/Connexions/rhaptos2.common.git
    git clone https://github.com/Connexions/atc.git
    cd $SRC/atc
    npm install .
    cd $ABSDIR

}


function inifile() {
    CONFIG=$VENV_REPO/develop.ini
    cp $SRC/rhaptos2.repo/develop.ini $CONFIG
    ATC_SRC=$SRC/atc
    sed -i -e "s,atc_directory = .*,atc_directory = $ATC_SRC,g" $CONFIG
    echo -e "========================================\n"
    echo "Source at: $SRC"
    echo "Virtual environment at: $VENV_REPO"
    echo "Wrote configuration file to: $CONFIG"
    echo -e "====================\n"
    echo "The following command is used to activate your virtual environment:"
    echo "cd $VENV_REPO; source bin/activate"
    echo -e "====================\n"
    echo "For future reference here are absolute paths to important resources:"
    echo "run script: $VENV_REPO/bin/rhaptos2repo-run"
    echo "config:     $CONFIG"
    echo -e "====================\n"
    echo "Use the following to run the repository:"
    echo "rhaptos2repo-run --debug --config=$CONFIG"
    echo -e "========================================\n"
}

### main:

TGTDIR=${1:-.}
ABSDIR=$( cd $TGTDIR ; pwd -P )
SRC=$ABSDIR/src
VENVS=$ABSDIR/venvs
VENV_REPO=$VENVS/vrepo

isempty $ABSDIR
echo "Downloading and installing the application in a virtual environment."
download_src
. $SRC/rhaptos2.repo/buildvenv.sh $VENV_REPO $SRC/rhaptos2.common  $SRC/rhaptos2.repo
# TODO We need to initialized the database. Is this in the scope of
#      this script?
inifile
