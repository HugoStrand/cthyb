
import numpy as np
from pytriqs.archive import HDFArchive
from triqs_cthyb import SolverCore
from pytriqs.gf import LegendreToMatsubara

results_file_name = "legendre.h5"

with HDFArchive(results_file_name,'r') as Results:
    S = Results['cthyb']

print dir(S)

nl = len(S.G_l.mesh)

from pytriqs.gf.tools import fit_legendre
G_l = fit_legendre(S.G_tau, order=nl)
G_l_smooth = fit_legendre(S.G_tau, order=20)

G_tau = S.G_tau.copy()
G_tau << LegendreToMatsubara(G_l)

G_tau_smooth = S.G_tau.copy()
G_tau_smooth << LegendreToMatsubara(G_l_smooth)

from pytriqs.plot.mpl_interface import oplot, oploti, oplotr, plt

plt.figure(figsize=(6, 8))
subp = [2, 1, 1]

plt.subplot(*subp); subp[-1] += 1
oplotr(S.G_tau['up'], alpha=0.5)
oplotr(G_tau['up'], alpha=0.5)
oplotr(G_tau_smooth['up'], alpha=0.5)
plt.ylim([-0.75, 0])

plt.subplot(*subp); subp[-1] += 1
plt.plot(np.squeeze(np.abs(S.G_l['up'].data)), 'o-')
plt.plot(np.squeeze(np.abs(G_l['up'].data)), 'x-')
plt.plot(np.squeeze(np.abs(G_l_smooth['up'].data)), 'x-')
plt.semilogy([], [])
plt.ylabel(r'$|G_l|$')
plt.xlabel(r'$l$')

plt.tight_layout()
plt.show()
