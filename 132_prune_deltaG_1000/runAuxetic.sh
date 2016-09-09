#!/bin/bash
#SBATCH --job-name=delG1k
#SBATCH --output=job0.out
#SBATCH --partition=boltzmann
#SBATCH --nodes=15
#SBATCH --exclusive
#SBATCH --mail-type=ALL
#SBATCH --mail-user=danielreid@uchicago.edu

set -e

THIS=$( dirname $0 )
if [ -e out ] 
then
	rm -r $PWD/out
fi
export PYTHONPATH=$PWD
#turns off output from run setup, joining
export TURBINE_LOG=0 
export TURBINE_OUTPUT=$PWD/out
export PATH=$PATH:/home/wozniak/Public/sfw/compute/gcc/swift-t-mpich-py/stc/bin:/home/wozniak/Public/sfw/compute/gcc/swift-t-mpich-py/turbine/bin:/home/danielreid/swift-auxetic/core/build/python/build/lib.linux-x86_64-2.7
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/danielreid/swift-auxetic/core/build
export PPN=12
export WALLTIME=30-00:00:00
export QUEUE=boltzmann
export PROJECT=pi-depablo
export TURBINE_JOBNAME=hello
#export TURBINE_SBATCH_ARGS="--time=10:00"
module load java
module load mvapich2

#module load gcc
#module load intel/15.0
module load boost/1.55+python-2.7-2014q1
which swift-t
nice swift-t  -n 204 -m slurm -p $THIS/tryAuxetic.c
#swift-t -n 2 -p $THIS/tryAuxetic.c  
#python drivers.py
