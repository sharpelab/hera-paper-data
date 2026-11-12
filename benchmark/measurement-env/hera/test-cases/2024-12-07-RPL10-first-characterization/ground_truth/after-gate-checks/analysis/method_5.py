
fig1, ax1 = plt.subplots()

for file in [4, 5]:
    data = sl.pload(file_path, file)
    I_tg = data['k_tg_curr']
    xs = data['xs']
    ax1.plot(xs[:len(I_tg)], I_tg)
ax1.axvline(-5.5)
ax1.axvline(6.)
ax1.set_xlabel('V_tg (V)')
ax1.set_ylabel('Leakage (A)')
