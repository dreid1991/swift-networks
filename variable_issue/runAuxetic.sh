#!/bin/bash

# source /srv/adm/modules/init/bash
# module load boost/1.55+python-2.7-2014q1
# module unload boost
# module load boost/1.58+python-2.7-2015q2

set -eu

GB_ROOT=$HOME/proj/gb
GB_CODE=$GB_ROOT/code
GB_BUILD=$GB_ROOT/build
export LD_LIBRARY_PATH+=:$GB_BUILD

THIS=$( dirname $0 )
export PYTHONPATH=
PYTHONPATH+=$THIS
PYTHONPATH+=:$( cd $THIS/.. ; /bin/pwd )
PYTHONPATH+=:$GB_BUILD/python/build/lib.linux-x86_64-2.7
PYTHONPATH+=:$GB_CODE

#turns off output from run setup, joining
export TURBINE_LOG=0

echo LLD: $LD_LIBRARY_PATH
echo PP: $PYTHONPATH

N=${1:-3}
set -x
swift-t -n $N -p $THIS/tryAuxetic.c
