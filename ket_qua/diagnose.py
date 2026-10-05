# For each saved model: how many fc1 ReLU units are ever active, and which greedy actions it picks
# on the first 3000 test steps. Run from smart-home-energy-trading-with-DRL/
# Usage: python ../ket_qua/diagnose.py saved_nets/run_a saved_nets/run_b ...
import os, sys, collections, contextlib, io
sys.path.insert(0, os.getcwd())
import numpy as np
import torch
import HEMS, env

for path in sys.argv[1:]:
    with contextlib.redirect_stdout(io.StringIO()):
        m = HEMS.HEMS(load=True, path=path)
    e = env.Env(m.df, m.battery, m.max_en, m.eff, m.price_coefs, m.n_days, 3000, low=30000, high=len(m.df), test=True)
    e.reset(0)
    alive = np.zeros(m.agent.eval_net.fc1.out_features, dtype=bool)
    acts = collections.Counter()
    with torch.no_grad():
        for _ in range(3000):
            s = torch.FloatTensor(e.next_observation_normalized()).unsqueeze(0)
            alive |= (m.agent.eval_net.fc1(s)[0] > 0).numpy()
            a = int(m.agent.eval_net(s).argmax())
            acts[a] += 1
            e.step(a)
    print(f"{path}\tfc1_alive={int(alive.sum())}/8\tgreedy_actions={dict(sorted(acts.items()))}")
