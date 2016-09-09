#!/bin/sh

set -e

THIS=$( dirname $0 )
export PYTHONPATH=$THIS
#turns off output from run setup, joining
export TURBINE_LOG=0 

swift-t -n 5 -p $THIS/tryAuxetic.c
