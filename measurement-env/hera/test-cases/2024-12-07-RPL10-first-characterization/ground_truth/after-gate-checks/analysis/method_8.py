
fig1, ax1 = plt.subplots()

for file in [7, 8]:
    data = sl.pload(file_path, file)
    I_tg = data['k_bg_curr']
    xs = data['xs']
    ax1.plot(xs[:len(I_tg)], I_tg)
ax1.axvline(-9)
ax1.axvline(5)
ax1.set_xlabel('V_bg (V)')
ax1.set_ylabel('Leakage (A)')
