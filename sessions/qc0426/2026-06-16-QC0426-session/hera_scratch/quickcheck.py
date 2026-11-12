import numpy as np, json
m=json.load(open("data/1/metadata.json")); idx={c:i for i,c in enumerate(m["columns"])}
print("interrupted:", m["interrupted"])
d=np.loadtxt("data/1/data.tsv"); 
I=d[-300:,idx["sr0_X"]]/(-1e6)
print("last-300pts drain I nA: med %.2f min %.2f max %.2f"%(np.median(I)*1e9,I.min()*1e9,I.max()*1e9))
print("leak so far: k_bg %.1e  k_2410 %.1e A"%(np.abs(d[:,idx["k_bg_curr"]]).max(),np.abs(d[:,idx["k_2410_curr"]]).max()))
print("rows:", d.shape[0], "fast-rows:", d.shape[0]//101)
