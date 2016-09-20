#!/bin/sh

set -e

THIS=$( dirname $0 )
export PYTHONPATH=$( cd $THIS/.. ; /bin/pwd )
#turns off output from run setup, joining
export TURBINE_LOG=0

N=${1:-5}
set -x
swift-t -n $N -p $THIS/tryAuxetic.c
