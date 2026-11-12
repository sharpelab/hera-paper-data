from hera.analysis import open_run, plot_raw
import matplotlib.pyplot as plt

r6, r7 = open_run('data/6'), open_run('data/7')
for r in (r6, r7):
    display(plot_raw(r))
    plt.close('all')
