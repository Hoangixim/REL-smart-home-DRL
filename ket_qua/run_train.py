# Train + save + full test one configuration; run from smart-home-energy-trading-with-DRL/
# Usage: python ../ket_qua/run_train.py <name> <max_en> [torch_seed]
# torch_seed only fixes the initial network weights (numpy is re-seeded inside env.reset by the original code).
import os, sys, time
sys.path.insert(0, os.getcwd())
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import HEMS

name, max_en = sys.argv[1], float(sys.argv[2])
torch.set_num_threads(1)  # tiny network; avoids CPU contention when several runs share the machine
if len(sys.argv) > 3:
    torch.manual_seed(int(sys.argv[3]))
print("TORCH_SEED", torch.initial_seed(), flush=True)
m = HEMS.HEMS(battery=20, max_en=max_en, eff=0.95, price_coefs=[2, 0.5], data_path="data/rtp.csv")
t = time.time()
m.train()
print("TRAIN_SECONDS", round(time.time() - t, 1), "epsilon", m.epsilon, flush=True)
m.save("saved_nets/" + name)
t = time.time()
r = m.test()
print("TEST_SECONDS", round(time.time() - t, 1))
print("RAW results [sRL, baseline1_alt, baseline2_nobatt, no_pv_no_batt]:", [float(x) for x in r])
plt.savefig("../ket_qua/" + name + ".png", dpi=80)
