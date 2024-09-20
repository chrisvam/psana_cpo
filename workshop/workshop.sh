#!/bin/bash

#SBATCH --partition=milano
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --output=%j.log

# see https://confluence.slac.stanford.edu/display/PCDS/Submitting+SLURM+Batch+Jobs

# "-u" flushes print statements which can otherwise be hidden if mpi hangs
# "-m mpi4py.run" allows mpi to exit if one rank has an exception
mpirun python -u -m mpi4py.run workshop.py
