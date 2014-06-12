#!/bin/env pytriqs

import numpy as np
import pytriqs.utility.mpi as mpi
from pytriqs.gf.local import *
from pytriqs.parameters.parameters import Parameters
from pytriqs.operators.operators2 import *
from pytriqs.archive import HDFArchive
from pytriqs.applications.impurity_solvers.cthyb import *
import itertools
from collections import OrderedDict

from pytriqs.plot.mpl_interface import plt, oplot
from matplotlib.backends.backend_pdf import PdfPages

def print_master(msg):
    if mpi.rank==0: print msg

print_master("Welcome to asymm_bath test (1 band with a small asymmetric hybridization function).")
print_master("This test helps to detect sampling problems.")

# H_loc parameters
beta = 40.0
ed = -1.0
U = 2.0

epsilon = [0.0,0.1,0.2,0.3,0.4,0.5]
V = 0.2

# Parameters
p = SolverCore.solve_parameters()
p["max_time"] = -1
p["random_name"] = ""
p["random_seed"] = 123 * mpi.rank + 567
p["verbosity"] = 3
p["length_cycle"] = 50
p["n_warmup_cycles"] = 20000
p["n_cycles"] = 1000000

# Block structure of GF
gf_struct = OrderedDict()
gf_struct['up'] = [0]
gf_struct['down'] = [0]

# Hamiltonian
H = ed*(n("up",0) + n("down",0)) + U*n("up",0)*n("down",0)

# Quantum numbers
qn = []
qn.append(n("up",0))
qn.append(n("down",0))
    
# Construct solver    
S = SolverCore(beta=beta, gf_struct=gf_struct, n_tau_g0=1000, n_tau_g=1000)

if mpi.rank==0:
    arch = HDFArchive('asymm_bath.h5','w')
    pp = PdfPages('G_asymm_bath.pdf')

# Set hybridization function
for e in epsilon:
    delta_w = GfImFreq(indices = [0], beta=beta)
    delta_w <<= (V**2) * inverse(iOmega_n - e)

    S.Delta_tau["up"] <<= InverseFourier(delta_w)
    S.Delta_tau["down"] <<= InverseFourier(delta_w)

    S.solve(h_loc=H, params=p)
  
    if mpi.rank==0:
        arch['epsilon_' + str(e)] = {"up":S.G_tau["up"], "down":S.G_tau["down"]}

        plt.clf()
        oplot(S.G_tau["up"], name="$\uparrow\uparrow$")
        oplot(S.G_tau["down"],name="$\downarrow\downarrow$")
        
        axes = plt.gca()
        axes.set_ylabel('$G(\\tau)$')
        axes.legend(loc='lower center',prop={'size':10})
        
        axes.set_title("$U=%.1f$, $\epsilon_d=%.1f$, $V=%.1f$, $\epsilon_k=%.1f$" % (U,ed,V,e))

        pp.savefig(plt.gcf())

if mpi.rank==0: pp.close()
