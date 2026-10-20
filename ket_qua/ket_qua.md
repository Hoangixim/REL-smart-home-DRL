# Kết quả chạy lại

Máy chạy: Windows 11, Python 3.13, torch 2.9 (CPU), numpy 2.2, pandas 2.2.
Sửa code gốc: chỉ 1 chỗ, `dqn.py:127-128` thêm `weights_only=False` (xem nhật ký trong `../HUONG_DAN.md`).

Lệnh đã chạy: xem `../HUONG_DAN.md` Phần 5. Biểu đồ được lưu bằng cách chạy với `MPLBACKEND=Agg` rồi gọi `plt.savefig(...)` sau `m.test()`, không sửa `fig.show()` trong code.

## 1. Model có sẵn của tác giả (`saved_nets/rtp_20_10_90_2_2`)

Cấu hình thật (theo `properties.json`): pin 20 kWh, `max_en=1` (≈ 4 kW), hiệu suất 95%, giá RTP, mua = 2×SMP, bán = 0.5×SMP (= ¼ giá mua, khớp bài báo), ε lúc test = 0.0176.

### Test full năm thứ 2 (dòng 30000 → hết, 29 844 bước) — 84 giây

| Chiến lược | Tên trong bài báo | Chi phí cả năm | DQN rẻ hơn |
|---|---|---|---|
| **DQN** | proposed | **1000.26** | — |
| Xoay vòng 4 action (`step % 4`) — "compare" | Baseline 2 – alternating | 1176.15 | **14.95%** |
| Có PV, không pin (action 7) | Baseline 1 – greedy | 1250.84 | **20.03%** |
| Không PV, không pin | (không có trong bài) | 1973.54 | 49.32% |

Số in ra gốc: `DQN cost:-1000.26 | compare cost:-1176.15 | Gain over compare: 175.89( 14.95% )` — dấu âm vì code cộng dồn `-tiền_trả`.

Biểu đồ: `pretrained_test_full.png`. Log: `pretrained_test_full.log`.

### Test nhanh 2000 bước — 59 giây (phần lớn là nạp `params.json` 95 MB)

DQN 89.89 · xoay vòng 104.00 (DQN rẻ hơn 13.57%) · không pin 108.45 · không PV không pin 172.22. Biểu đồ: `pretrained_test_2000.png`.

## 2. Số liệu chính xác của bài báo (Fig. 3 và Fig. 4)

**Cách lấy:** Fig. 3/4 được nhúng trong PDF dưới dạng vector (pgfplots, file gốc `results_rtp.pdf`, `results_tou2.pdf`). Mình đọc toạ độ từng cột (lệnh `re`) và vị trí các vạch lưới trục y, rồi quy đổi tuyến tính sang €. Kết quả ra số tròn và khớp mọi con số ghi trong bài (730 €, 894 €, −41.60%, −40.68%, −47.66%; −35.27% tính lại ra 35.23% do làm tròn) ⇒ tin cậy được. Trang PDF được render bằng API `Windows.Data.Pdf` có sẵn của Windows để xem bằng mắt; ảnh cắt: `paper_fig2_prices.png`, `paper_fig3_rtp.png`, `paper_fig4_tou.png`, `paper_fig5_selfbalancing.png`.

**Fig. 3 — RTP, chi phí năm test (€):**

| Pin, hiệu suất | DQN 6 kW | DQN 4 kW | Baseline 2 xoay vòng (6 kW) | Baseline 1 không pin |
|---|---|---|---|---|
| 20 kWh, 80% | 1037 | 1094 | 1411 | 1250 |
| 10 kWh, 80% | 1050 | 1106 | 1407 | 1250 |
| 20 kWh, 90% | 876 | 1052 | 1212 | 1250 |
| 10 kWh, 90% | 910 | 1069 | 1212 | 1250 |
| **20 kWh, 95%** | **730** | **976** | **1127** | **1250** |
| 10 kWh, 95% | 766 | 998 | 1129 | 1250 |

**Fig. 4 — TOU (`tou2.csv`), chi phí năm test (€):**

| Pin, hiệu suất | DQN 6 kW | DQN 4 kW | Baseline 2 xoay vòng (6 kW) | Baseline 1 không pin |
|---|---|---|---|---|
| 20 kWh, 80% | 1384 | 1484 | 1928 | 1708 |
| 10 kWh, 80% | 1386 | 1484 | 1920 | 1708 |
| 20 kWh, 90% | 1113 | 1443 | 1634 | 1708 |
| 10 kWh, 90% | 1124 | 1450 | 1632 | 1708 |
| 20 kWh, 95% | 894 | 1279 | 1507 | 1708 |
| 10 kWh, 95% | 915 | 1291 | 1509 | 1708 |

Lưu ý: bài chỉ vẽ Baseline 2 với 6 kW, không có cột xoay vòng 4 kW.

### So với bài báo (model có sẵn = cấu hình 20 kWh / 95% / 4 kW)

| | Bài báo (Fig. 3) | Chạy lại model có sẵn | Lệch |
|---|---|---|---|
| DQN 4 kW | 976 | 1000.26 | +2.5% |
| Baseline 1 không pin | 1250 | 1250.84 | ≈ 0 (khớp) |
| Xoay vòng | 1127 (6 kW) | 1176.15 (4 kW) | khác cấu hình, không so trực tiếp |

- Baseline 1 khớp gần tuyệt đối ⇒ môi trường mô phỏng, dữ liệu và cách tính tiền **tái hiện đúng**.
- DQN lệch +2.5%: hợp lý vì lúc test vẫn còn ε ≈ 0.018 ngẫu nhiên (chạy lại sẽ ra số lệch nhẹ), và không chắc đây đúng là model tác giả dùng để vẽ hình.

## 3. Train lại từ đầu

Script: `run_train.py` (train 200 episode → lưu → test full năm → lưu biểu đồ), không sửa code gốc. Cấu hình chung: pin 20 kWh, hiệu suất 95%, giá RTP, `price_coefs=[2, 0.5]`, mọi siêu tham số giữ nguyên như code gốc. ε cuối = 0.0176 ở mọi run (khớp model có sẵn).

- `try5`: 5 episode, 16.5 s — chỉ để đo tốc độ.
- 4 run đầu (`run_4kw_1/2`, `run_6kw_1/2`): seed torch ngẫu nhiên, 4 run chạy song song mỗi run 12 luồng → ~26 phút/run.
- 8 run sau (`*_s1..s4`): seed torch cố định 1–4 (chỉ quyết định trọng số khởi tạo; numpy đã được code gốc seed bên trong `env.reset`), `torch.set_num_threads(1)`, 8 run song song → ~15 phút/run. **Tái lập được**: chạy lại cùng seed ra cùng kết quả.
- Test mỗi model: ~85–95 s.

### Kết quả (chi phí năm test, €; % âm = DQN rẻ hơn)

**4 kW** — baseline: xoay vòng 1176.15 · không pin 1250.84 · bài báo DQN = **976**

| Run | Seed | DQN | vs xoay vòng | vs không pin | Nơ-ron fc1 sống | Action greedy (3000 bước đầu) |
|---|---|---|---|---|---|---|
| *model có sẵn* | — | **1000.26** | −14.95% | −20.03% | 1/8 | 0: 722, 1: 2278 |
| run_4kw_1 | ngẫu nhiên | 1249.30 | +6.22% | −0.12% | 0/8 | chỉ 3 |
| run_4kw_2 | ngẫu nhiên | 1249.30 | +6.22% | −0.12% | 0/8 | chỉ 3 |
| run_4kw_s1 | 1 | 1231.67 | +4.72% | −1.53% | 0/8 | chỉ 1 |
| run_4kw_s2 | 2 | **1166.51** | **−0.82%** | −6.74% | 1/8 | 1: 800, 2: 780, 3: 1420 |
| run_4kw_s3 | 3 | 1245.12 | +5.86% | −0.46% | 2/8 | 1: 86, 3: 2914 |
| run_4kw_s4 | 4 | 1231.67 | +4.72% | −1.53% | 0/8 | chỉ 1 |

**6 kW** — baseline: xoay vòng 1127.32 (bài báo: 1127 ✓) · không pin 1250.84 (bài báo: 1250 ✓) · bài báo DQN = **730**

| Run | Seed | DQN | vs xoay vòng | vs không pin | Nơ-ron fc1 sống | Action greedy |
|---|---|---|---|---|---|---|
| run_6kw_1 | ngẫu nhiên | 1221.64 | +8.37% | −2.33% | 0/8 | chỉ 1 |
| run_6kw_2 | ngẫu nhiên | 1249.12 | +10.80% | −0.14% | 0/8 | chỉ 3 |
| run_6kw_s1 | 1 | 1221.64 | +8.37% | −2.33% | 0/8 | chỉ 1 |
| run_6kw_s2 | 2 | **994.32** | **−11.80%** | **−20.51%** | 1/8 | 1: 617, 2: 2383 |
| run_6kw_s3 | 3 | 1249.12 | +10.80% | −0.14% | 1/8 | chỉ 3 |
| run_6kw_s4 | 4 | 1249.12 | +10.80% | −0.14% | 0/8 | chỉ 3 |

(Cột nơ-ron/action đo bằng `diagnose.py`: chạy greedy 3000 bước test đầu, đếm nơ-ron ReLU lớp 1 có lúc nào > 0.)

### Nhận xét

1. **Môi trường tái hiện chính xác**: 2 baseline khớp số bài báo gần tuyệt đối (1250.84 vs 1250; 1127.32 vs 1127).
2. **Train lại rất bấp bênh**: 12 run → chỉ **1/6 run 6 kW** và **1/6 run 4 kW** thắng chiến lược xoay vòng; đa số chỉ ngang "không dùng pin". Khớp với cảnh báo trong README gốc ("có thể phải train lại hơn 10 lần").
3. **Nguyên nhân: "dying ReLU"** — lớp 1 chỉ có 8 nơ-ron nhận 1344 đầu vào, lr = 0.01, reward lớn (R1 tới −15, R2 ×10 so với bài) ⇒ trong lúc train cả 8 nơ-ron bị đẩy về vùng âm, mạng trả **hằng số** cho mọi state ⇒ luôn chọn 1 action (1 hoặc 3 = luôn xả pin) ⇒ pin luôn ~0 ⇒ chi phí ≈ không pin. Run nào thắng đều còn ≥ 1 nơ-ron sống; ngay cả model có sẵn của tác giả cũng chỉ còn 1/8.
4. Các run "chết" cho kết quả **trùng nhau từng chữ số** dù seed khác (vd. 1249.12 ×3) vì chính sách hằng số + numpy được code gốc seed cố định khi test.
5. Run tốt nhất 6 kW (994.32) vẫn **còn xa 730 € của bài báo** (−11.8% vs −35.2% so với xoay vòng). Model có sẵn 4 kW (1000.26) thì gần cột 976 € của bài. ⇒ Tái hiện được **xu hướng** (DQN thắng baseline khi train thành công) nhưng **không tái hiện được con số tốt nhất** chỉ với 6 lần thử mỗi cấu hình.

Biểu đồ: `run_*.png` (vd. `run_6kw_s2.png` — run tốt nhất, pin dao động 10–19 kWh; `run_4kw_1.png` — run chết, pin luôn ~0). Log: `run_*.log`.

## 4. Train bổ sung seed 5–12 cho cấu hình 6 kW

Cấu hình chung: pin 20 kWh, hiệu suất 95%, giá RTP, `price_coefs=[2, 0.5]`, `max_en=1.5`. Mỗi run huấn luyện 200 episode và đánh giá trên toàn bộ năm kiểm thử (29 844 bước).

### Kết quả (DQN Result, Baseline và Gain)

| Run | Seed | DQN Result | Baseline | Gain | Gain (%) |
|---|---:|---:|---:|---:|---:|
| phase2_seed5_6kw | 5 | -1260.58 | -1127.32 | -133.25 | -11.82% |
| phase2_seed6_6kw | 6 | -1241.61 | -1127.32 | -114.29 | -10.14% |
| phase2_seed7_6kw | 7 | -1221.64 | -1127.32 | -94.32 | -8.37% |
| phase2_seed8_6kw | 8 | -980.60 | -1127.32 | +146.72 | +13.01% |
| phase2_seed9_6kw | 9 | -1221.64 | -1127.32 | -94.32 | -8.37% |
| phase2_seed10_6kw | 10 | -1249.12 | -1127.32 | -121.79 | -10.80% |
| phase2_seed11_6kw | 11 | -1204.14 | -1127.32 | -76.82 | -6.81% |
| phase2_seed12_6kw | 12 | -1227.81 | -1127.32 | -100.49 | -8.91% |

### Thống kê và nhận xét

- 8 run được thực hiện với seed từ 5 đến 12.
- Chỉ 1/8 run (12,5%) tốt hơn Baseline: `phase2_seed8_6kw`, Gain = +13,01%.
- Gain trung bình của 8 run: khoảng -6,53%.
- Run tốt nhất: seed 8, DQN Result = -980,60.
- Run kém nhất theo Gain: seed 5, Gain = -11,82%.

Kết quả cho thấy hiệu suất DQN chưa ổn định giữa các seed. Phần lớn run chưa vượt Baseline, do đó cần tiếp tục phân tích hành vi chọn action và quá trình học để tìm nguyên nhân.

Mục tiêu tìm kết quả gần 730 € chưa đạt được trong nhóm run này. Giá trị DQN Result tốt nhất là -980,60 theo cách chương trình ghi nhận; không nên coi đây là chi phí dương 980,60 € nếu chưa đối chiếu quy ước dấu của chương trình.

### File kết quả

- Bảng CSV: `phase2_item7_results.csv`
- Bảng Excel: `phase2_item7_results.xlsx`
- Biểu đồ: `phase2_seed5_6kw.png` đến `phase2_seed12_6kw.png`

### Công thức

- `Gain = Baseline - DQN Result`
- `Gain (%) = Gain / abs(Baseline) × 100`

