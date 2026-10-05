# Hướng dẫn REL: hiểu bài báo và chạy lại code

> Bài báo: **Pokorn et al., "Smart Home Energy Cost Minimisation Using Energy Trading with Deep Reinforcement Learning"**, BuildSys '23 (5 trang).
> Code: thư mục [smart-home-energy-trading-with-DRL/](smart-home-energy-trading-with-DRL/), gồm 3 file Python, tổng khoảng 800 dòng.
>
> Đọc theo thứ tự: **Phần 1 → 2 → 3** để hiểu, rồi làm theo **Phần 5** để chạy. Phần 4 là tư liệu cho báo cáo.

---

## Phần 1: Bài báo nói gì (đọc trong 2 phút)

**Bối cảnh.** Một ngôi nhà có:
- **pin mặt trời (PV)** để tự sản xuất điện,
- **pin lưu trữ** (battery, 10 hoặc 20 kWh),
- kết nối **lưới điện**, nơi có thể **mua** điện và **bán** điện. Giá điện thay đổi theo thời gian.

**Bài toán.** Cứ mỗi 15 phút phải quyết định nên sạc pin hay xả pin, mua điện hay bán điện, sao cho **tổng tiền điện cả năm thấp nhất**. Ngôi nhà không bật/tắt thiết bị, chỉ điều khiển dòng điện.

**Cách giải.** Dùng **DQN** (Deep Q-Network), một thuật toán RL kinh điển. Agent nhìn **2 ngày lịch sử gần nhất** rồi chọn **1 trong 4 hành động**.

**Kết quả trong bài.**
- Với giá RTP (real-time): chi phí khoảng **730 €/năm**, thấp hơn 2 baseline lần lượt **35.27%** và **41.60%**.
- Với giá TOU (theo khung giờ): khoảng **894 €/năm**, thấp hơn **40.68%** và **47.66%**. Con số 47.66% được ghi trong abstract.

**Dữ liệu.** Đo thật tại một nhà thông minh ở Thessaloniki (Hy Lạp), từ 10/2018 đến 10/2020, mỗi 15 phút một dòng, tổng **59 844 dòng**.
- Năm đầu dùng để **train**, năm sau dùng để **test**.
- Dữ liệu **đã có sẵn** trong `data/`, không phải tải thêm.

---

## Phần 2: Kiến thức RL tối thiểu cần nắm

Bạn chỉ cần hiểu 6 khái niệm dưới đây, mỗi khái niệm có chỗ tương ứng trong code.

| Khái niệm | Ý nghĩa ngắn | Trong code ở đâu |
|---|---|---|
| **State** *s* | Agent "nhìn thấy" gì để quyết định | `next_observation_normalized()`, [env.py:76](smart-home-energy-trading-with-DRL/env.py#L76) |
| **Action** *a* | Agent được làm gì | `take_action()`, [env.py:131](smart-home-energy-trading-with-DRL/env.py#L131) |
| **Reward** *r* | Điểm thưởng/phạt sau mỗi bước, agent cố tối đa tổng điểm | `my_reward = ...`, [HEMS.py:107](smart-home-energy-trading-with-DRL/HEMS.py#L107) |
| **Q(s, a)** | Ước lượng "chọn a ở trạng thái s thì về lâu dài được bao nhiêu điểm". DQN dùng mạng nơ-ron để xấp xỉ Q | class `Net`, [dqn.py:22](smart-home-energy-trading-with-DRL/dqn.py#L22) |
| **Epsilon-greedy** | Với xác suất ε thì chọn ngẫu nhiên để **khám phá**, còn lại chọn action có Q lớn nhất | `choose_action()`, [dqn.py:55](smart-home-energy-trading-with-DRL/dqn.py#L55) |
| **Replay buffer + Target net** | 2 "mẹo" giúp DQN học ổn định: lưu kinh nghiệm cũ rồi lấy mẫu ngẫu nhiên để học; dùng một bản sao mạng cập nhật chậm để tính mục tiêu | `store_transition()` và `learn()`, [dqn.py:68-97](smart-home-energy-trading-with-DRL/dqn.py#L68-L97) |

**Công thức cốt lõi của DQN** (nằm ở [dqn.py:90-93](smart-home-energy-trading-with-DRL/dqn.py#L90-L93)):

```
mục tiêu   = r + γ · max_a' Q_target(s', a')      (γ = 0.9)
loss       = (Q_eval(s, a) − mục tiêu)²           → Adam cập nhật Q_eval
```

**Chỗ khác với deep learning thông thường:** không có "bộ dữ liệu có nhãn".
1. Agent tự đi trong môi trường mô phỏng, được dựng từ file CSV.
2. Agent tự sinh kinh nghiệm `(s, a, r, s')` và lưu vào buffer.
3. Agent học từ chính kinh nghiệm đó.

File CSV chỉ cung cấp "thế giới": điện mặt trời sinh ra, điện nhà dùng và giá điện theo thời gian.

---

## Phần 3: Bản đồ bài báo ↔ code

### 3.1. State: bài báo dùng 5 biến, code dùng 7 biến

Mỗi biến là một chuỗi **192 giá trị** (2 ngày × 96 bước), nối lại thành một vector.

| Biến | Bài báo (công thức 9) | Code |
|---|---|---|
| Mức pin | ✓ | ✓ |
| Điện PV sinh ra | ✓ | ✓ |
| Điện nhà tiêu thụ | ✓ | ✓ |
| Giá điện | ✓ | ✓ |
| Chi phí từng bước | ✓ | ✓ |
| Điện sạc xe điện (`EV_Consumption`) | ✗ | ✓ |
| Thời điểm trong ngày (`Time_of_Day`) | ✗ | ✓ |
| **Kích thước đầu vào mạng** | 5 × 192 = **960** | 7 × 192 = **1344** |

### 3.2. Action: 4 hành động

Quy tắc chung: điện PV **luôn được dùng cho nhà trước**. Action chỉ quyết định phần dư hoặc phần thiếu.

| Bài báo | Code | Ý nghĩa |
|---|---|---|
| (1) | `action 0` | Mua điện lưới cho nhà; **sạc pin hết cỡ** (bằng PV dư, thiếu thì mua thêm từ lưới) |
| (2) | `action 1` | Pin cấp cho nhà; **pin còn dư thì bán** lên lưới; PV dư cũng bán |
| (3) | `action 2` | Mua lưới cho nhà; PV dư thì sạc pin, còn dư nữa thì bán |
| (4) | `action 3` | Pin cấp cho nhà (không bán từ pin); PV dư bán hết |

`env.py` còn có thêm action 4–7, nhưng agent **không dùng**. Action 7 ("không có pin") được dùng cho một baseline, xem mục 3.5.

### 3.3. Reward: 3 thành phần (công thức 10–13 ↔ [HEMS.py:107-109](smart-home-energy-trading-with-DRL/HEMS.py#L107-L109))

| Thành phần | Bài báo | Code | Ý nghĩa |
|---|---|---|---|
| R1 | công thức (11), α=0.1, β=0.8 | `battery_penalty_expand(capacity, 20, 0.1, 0.8)` | Pin trong khoảng 10–80% thì +1. Pin quá cạn bị phạt nhẹ. **Pin quá đầy bị phạt nặng**: đầy 100% cho R1 = −15 |
| R2 | công thức (12), γ=3 | `3 * slope_market_price(...)` | Thưởng khi **sạc lúc giá thấp hơn median** và **xả lúc giá cao hơn median**. Median tính trong cửa sổ 2 ngày |
| R3 | công thức (13), δ=3 | `3 * reward`, với `reward = -amount_paid` | Tiền điện của bước đó. Trả càng nhiều thì điểm càng âm |

R1 và R2 là **reward shaping**: chúng "gợi ý" cho agent học nhanh hơn. Mục tiêu thật vẫn là R3, tức tiền điện.

### 3.4. Mạng nơ-ron và siêu tham số

| | Bài báo | Code ([dqn.py:7-13](smart-home-energy-trading-with-DRL/dqn.py#L7-L13)) |
|---|---|---|
| Kiến trúc | 2 lớp ẩn × 8 nơ-ron, ReLU, Adam | `1344 → 8 → 8 → 4` |
| Learning rate, γ, batch, buffer, target update | **Không ghi** | 0.01, 0.9, 32, 2000, 100 |
| Số episode | 200 episode, mỗi episode 7 ngày | `n_episodes=200`, `n_steps=672` (= 7 × 96) |
| ε (tỉ lệ chọn ngẫu nhiên) | Không ghi | Bắt đầu từ 1, nhân 0.98 sau mỗi episode. Sau 200 episode còn **0.0176**, khớp đúng với model có sẵn |

### 3.5. Baseline (để so sánh): code **đặt tên ngược** với bài báo ⚠️

| Chiến lược | Tên trong bài báo | Tên trong code |
|---|---|---|
| Có PV, **không có pin** (action 7) | **Baseline 1 – greedy** | `baseline 2` (biến `env2`) |
| Lần lượt xoay vòng 4 action (`step % 4`) | **Baseline 2 – alternating** | `baseline 1` (biến `env1`), cũng chính là **"compare cost"** được in ra |

Ngoài ra code còn vẽ thêm đường **"no PV, no battery cost"**: chi phí nếu nhà không có PV lẫn pin.

### 3.6. Chia train/test và cấu hình hệ thống

- **Train:** dòng 0 → 29 999 (10/2018 → 06/09/2019). Mỗi episode lấy ngẫu nhiên một tuần trong khoảng này.
- **Test:** dòng 30 000 → hết (≈ 29 844 bước, khoảng 1 năm). Agent chỉ hành động, không học nữa.
- **Công suất pin:** bài báo ghi theo kW, code ghi theo **kWh mỗi 15 phút**:

  | Bài báo | Code (`max_en`) |
  |---|---|
  | 6 kW | 1.5 |
  | 4 kW | 1 |

- **Giá điện:**

  | | Bài báo | Code |
  |---|---|---|
  | Giá mua | 2 × SMP | `price_coefs[0] = 2` (giống bài báo) |
  | Giá bán | ¼ giá mua = 0.5 × SMP | `price_coefs[1]`: **mặc định là 1** (khác bài báo); model có sẵn dùng **0.5** (khớp bài báo) |

- **File giá:**
  - `data/rtp.csv`: giá RTP.
  - `data/tou2.csv`: giá TOU, khớp bài báo (SMP 0.06/0.075/0.09 → giá mua 0.12/0.15/0.18 €).
  - `data/tou.csv`: biến thể TOU khác, SMP chỉ dao động 0.07–0.08.

---

## Phần 4: Những chỗ code lệch so với bài báo (đưa vào báo cáo)

1. State có 7 biến thay vì 5 (thêm EV và giờ trong ngày), xem mục 3.1.
2. Tên baseline 1 và 2 bị đổi chỗ, xem mục 3.5.
3. Giá bán mặc định trong code (`price_coefs=[2,1]`) khác bài báo (`[2, 0.5]`). Muốn train giống bài báo phải truyền `price_coefs=[2,0.5]`.
4. **R2 (công thức 12):** bài báo chia cho dung lượng pin B và dùng **giá mua** (= 2×SMP); code **không chia B** và dùng **SMP gốc** ⇒ với B = 20, R2 trong code **lớn gấp 10 lần** công thức trong bài (2/20 = 1/10).
5. Lúc test, agent vẫn còn ε ≈ 0.018, tức khoảng 2% số bước chọn **ngẫu nhiên**. Vì vậy chạy test 2 lần sẽ ra số hơi khác nhau.
6. Pin còn dư ở bước cuối được quy ra tiền theo **SMP × 1** (không phải giá bán). Phép quy đổi này chỉ áp dụng cho DQN và chiến lược xoay vòng.
7. Tên thư mục model có sẵn `rtp_20_10_90_2_2` không khớp cấu hình thật. Cấu hình thật trong `properties.json`: pin 20 kWh, `max_en=1` (≈4 kW), hiệu suất 95%, giá `[2, 0.5]`.
8. Bài báo không ghi các siêu tham số DQN, chỉ code mới có (mục 3.4).
9. Không seed torch, nên kết quả train dao động mạnh. README gốc thừa nhận có thể phải train lại **hơn 10 lần** mới được model tốt. Đã kiểm chứng: 12 run → chỉ 2 run thắng baseline; nguyên nhân là **dying ReLU** (8 nơ-ron lớp 1 chết hết → mạng trả hằng số → luôn xả pin). Chi tiết ở [ket_qua/ket_qua.md](ket_qua/ket_qua.md) mục 3.
10. **R1 (công thức 11):** công thức in trong bài có vẻ bị **đảo** — biểu thức chứa α (ngưỡng dưới) lại gán cho điều kiện "pin > βB" và ngược lại. Code (`battery_penalty_expand`, với x = E_b/B):
    - x < α: −2(1 − x/α)² (pin cạn → phạt tối đa −2)
    - x > β: −16((x − β)/(1 − β))² (pin đầy → phạt tối đa −16; bài ghi hệ số −4 hoặc −2)
    - và **luôn cộng thêm +1** (bài không có) ⇒ pin trong vùng an toàn được thưởng +1 mỗi bước.
11. Trong bài, Baseline 2 (xoay vòng) chỉ được vẽ với **6 kW**; muốn so 4 kW thì dùng số "compare" do code in ra.

---

## Phần 5: Việc cần làm (checklist)

Mọi lệnh đều chạy trong **terminal của VS Code** (PowerShell).

- **Mỗi khối lệnh: copy cả khối**, dán vào terminal rồi Enter.
- Dòng đầu luôn là `cd` vào thư mục code. Nếu bỏ dòng này, code báo `FileNotFoundError: data/rtp.csv` hoặc `No module named 'env'`.

> **Tiến độ (05/10/2026):** Bước 1–6 ✅ đã chạy xong (12 run train). Kết quả + số liệu chính xác của Fig. 3/4 bài báo ở [ket_qua/ket_qua.md](ket_qua/ket_qua.md). Còn lại: Bước 7 (tuỳ chọn), Bước 8 (báo cáo).
>
> **Mẹo lưu biểu đồ mà không sửa code:** thêm `$env:MPLBACKEND = "Agg"` trước lệnh, và nối `; import matplotlib.pyplot as plt; plt.savefig('../ket_qua/ten.png')` vào cuối chuỗi `python -c`.

### ☑ Bước 1: Sửa lỗi tương thích torch (bắt buộc trước khi load model)

Torch mới (≥ 2.6) chặn việc load model kiểu cũ. Cần thêm `weights_only=False` vào **2 dòng** [dqn.py:127-128](smart-home-energy-trading-with-DRL/dqn.py#L127-L128):

```python
self.eval_net = torch.load(path + '/eval_net.pt', map_location=torch.device('cpu'), weights_only=False).to(device)
self.target_net = torch.load(path + '/target_net.pt', map_location=torch.device('cpu'), weights_only=False).to(device)
```

**Đã sửa sẵn trong repo này** (commit "Fix torch.load…"), đã ghi vào nhật ký sửa code ở cuối file.

### ☑ Bước 2: Chạy thử model có sẵn trên 2000 bước (khoảng 3 tuần dữ liệu)

```powershell
cd smart-home-energy-trading-with-DRL   # chạy từ thư mục gốc của repo
python -c "import HEMS; m=HEMS.HEMS(load=True, path='saved_nets/rtp_20_10_90_2_2'); m.test(steps=2000)"
```

**Kết quả mong đợi:**
- `False` và `cpu`: máy không có GPU, bình thường.
- Một khối chữ in hoa `YOU HAVE INITIALISED YOUR HEMS...` liệt kê cấu hình (pin 20 kWh, hiệu suất 95%…).
- `--- TESTING ---`, sau đó là thanh tiến trình chạy tới 2000.
- Dòng cuối có dạng:
  `Episode:Testing episode: ... | Epsilon: 0.02 | DQN cost: … | compare cost: … | Gain over compare: … ( …% )`
- Có thể một cửa sổ biểu đồ hiện lên rồi tắt ngay. Đây là lỗi `fig.show()` đã biết, không ảnh hưởng tới số liệu.

**Dấu hiệu sai:**
- `WeightsUnpickler error`: chưa làm Bước 1.
- `FileNotFoundError`: chưa `cd` đúng thư mục.

### ☑ Bước 3: Đọc đúng dòng kết quả ⚠️

Dòng kết quả có một bẫy: **"DQN cost" thực ra là *âm* của chi phí**. Code cộng dồn `reward = -tiền_trả`.

| Thấy in ra | Nghĩa thật |
|---|---|
| `DQN cost: -50` | Agent tốn **50** đơn vị tiền |
| `compare cost` | Chi phí (cũng mang dấu âm) của chiến lược **xoay vòng 4 action**, tức Baseline 2 trong bài báo |
| `Gain over compare` **dương** | DQN **tốt hơn** baseline |

### ☑ Bước 4: Test model có sẵn trên toàn bộ năm test

Bỏ tham số `steps` để chạy hết ≈ 29 844 bước, lâu hơn Bước 2 khoảng 15 lần:

```powershell
cd smart-home-energy-trading-with-DRL   # chạy từ thư mục gốc của repo
python -c "import HEMS; m=HEMS.HEMS(load=True, path='saved_nets/rtp_20_10_90_2_2'); m.test()"
```

→ Đây là con số để so với hình 3 của bài báo, theo cột pin 20 kWh, hiệu suất 95%, công suất 4 kW (bài báo: **976 €**, đọc chính xác từ dữ liệu vector của hình — xem [ket_qua/ket_qua.md](ket_qua/ket_qua.md)). Muốn giữ biểu đồ thì dùng mẹo `MPLBACKEND=Agg` + `plt.savefig` ở đầu Phần 5, không cần sửa code.

### ☑ Bước 5: Train thử 5 episode để đo thời gian

```powershell
cd smart-home-energy-trading-with-DRL   # chạy từ thư mục gốc của repo
python -c "import HEMS; m=HEMS.HEMS(price_coefs=[2,0.5]); m.train(n_episodes=5); m.save('saved_nets/try5')"
```

- **Mong đợi:**
  - Thanh tiến trình `Trainig in progress...` chạy 5 nấc.
  - Sau đó in ra `model saved to location: saved_nets/try5`.
  - Ghi lại tổng thời gian chạy rồi nhân 40 để ước lượng thời gian cho 200 episode.
- **Lưu ý:**
  - 5 episode là quá ít. Agent gần như chưa học được gì vì ε vẫn ≈ 0.9; lệnh này **chỉ để đo thời gian**.
  - Nếu thư mục lưu đã tồn tại, code in `Path already exists` và **không lưu**. Đổi tên thư mục rồi chạy lại.

### ☑ Bước 6: Train đầy đủ 200 episode rồi test

Mình đã viết sẵn script [ket_qua/run_train.py](ket_qua/run_train.py): train 200 episode → lưu model → test full năm → lưu biểu đồ. Cấu hình cố định: pin 20 kWh, hiệu suất 95%, giá `[2, 0.5]`, RTP; tham số thứ 2 là `max_en` (`1` = 4 kW, `1.5` = 6 kW). Mỗi run mất khoảng 15–20 phút.

```powershell
cd smart-home-energy-trading-with-DRL   # chạy từ thư mục gốc của repo
python ../ket_qua/run_train.py run_4kw_3 1
```

- **Mong đợi:** dòng `TRAIN_SECONDS ... epsilon 0.0175...`, `model saved to location: saved_nets/run_4kw_3`, dòng `Episode:Testing episode ...`, và file `ket_qua/run_4kw_3.png`.
- **Dấu hiệu sai:** `Path already exists` — tên run đã dùng, đổi số cuối.

- Kết quả dao động mạnh giữa các lần chạy, xem Phần 4 mục 9.
- Nên chạy **vài lần** (run1, run2, run3…) và ghi lại mọi kết quả, kể cả lần kém.

### ☐ Bước 7 (tuỳ chọn, để báo cáo có thêm điểm)

- **Thử giá TOU:** thêm `data_path='data/tou2.csv'` vào `HEMS(...)` rồi so với hình 4 của bài báo.
- **Thử cấu hình pin khác như bài báo:**
  - `battery=10` hoặc `battery=20`,
  - `max_en=1` hoặc `max_en=1.5`,
  - `eff=0.8`, `0.9` hoặc `0.95`.

### ☐ Bước 8: Viết báo cáo, gồm:

1. Tóm tắt bài toán (Phần 1).
2. Mô hình MDP: state/action/reward (Phần 3).
3. Môi trường chạy (Python 3.13, torch 2.9 CPU) và **danh sách sửa code**.
4. Bảng kết quả **bài báo vs chạy lại**.
5. Nhận xét chỗ lệch (Phần 4) và lý do kết quả khác.

---

## Phần 6: Câu hỏi tự kiểm tra (thầy hay hỏi kiểu này)

1. Tại sao cần **replay buffer**? Nếu học ngay từng bước liên tiếp thì có vấn đề gì?
2. Target net được cập nhật mỗi bao nhiêu lần `learn()`? Nó giải quyết vấn đề gì?
3. Agent bắt đầu học từ khi nào? Gợi ý: xem điều kiện `memory_counter > 2000` ở [HEMS.py:124](smart-home-energy-trading-with-DRL/HEMS.py#L124). Như vậy khoảng vài episode đầu agent chưa học gì.
4. Bỏ R1 (phạt pin) thì agent dễ học ra hành vi gì? Bỏ R2 thì sao?
5. Vì sao test vẫn có tính ngẫu nhiên? Muốn test hoàn toàn greedy thì sửa ở đâu?
6. Vì sao input mạng là 1344 chiều? Nếu đổi `n_days=1` thì bao nhiêu chiều?
7. γ = 0.9 nghĩa là agent "nhìn xa" khoảng bao nhiêu bước? Gợi ý: ≈ 1/(1−γ) = 10 bước = 2.5 giờ. Như vậy có đủ để "sạc trưa, bán tối" không?

---

## Phần 7: Thuật ngữ

| Từ | Nghĩa |
|---|---|
| **HEMS** | Home Energy Management System: hệ thống quản lý năng lượng trong nhà |
| **PV** | Photovoltaic: pin mặt trời |
| **SMP** | System Marginal Price: giá điện thị trường trong dataset |
| **RTP** | Real-Time Pricing: giá thay đổi liên tục theo thị trường |
| **TOU** | Time-Of-Use: giá theo khung giờ (cao điểm / bình thường / thấp điểm) |
| **Episode** | Một lượt chơi; ở đây là 1 tuần = 672 bước 15 phút |
| **Baseline** | Chiến lược đơn giản dùng để so sánh |
| **Reward shaping** | Thêm thưởng/phạt phụ để agent học dễ hơn |

---

## Mẫu nhật ký sửa code (điền dần)

| # | File:dòng | Sửa gì | Vì sao |
|---|---|---|---|
| 1 | `dqn.py:127-128` | Thêm `weights_only=False` vào `torch.load` | torch ≥ 2.6 mặc định `weights_only=True`, không load được nguyên `nn.Module` |
| 2 | | | |
