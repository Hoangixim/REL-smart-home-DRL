# REL — Reimplement: Smart Home Energy Trading with DRL

Đồ án môn **Reinforcement Learning (REL)**: chạy lại và phân tích code của bài báo

> M. Pokorn, M. Mohorčič, A. Čampa, J. Hribar. *Smart Home Energy Cost Minimisation Using Energy Trading with Deep Reinforcement Learning.* BuildSys '23. DOI: [10.1145/3600100.3625684](https://doi.org/10.1145/3600100.3625684)

Code gốc: [sensorlab/smart-home-energy-trading-with-DRL](https://github.com/sensorlab/smart-home-energy-trading-with-DRL) (MIT license), commit `0905df3`.

## 👉 Tiến độ nhóm: [TIEN_DO.md](TIEN_DO.md)

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| [TIEN_DO.md](TIEN_DO.md) | Bảng việc: ai làm gì, đang tới đâu — **cập nhật mỗi khi xong việc** |
| [HUONG_DAN.md](HUONG_DAN.md) | Hướng dẫn hiểu bài báo + code, bản đồ bài báo ↔ code, các chỗ code lệch bài báo, checklist chạy |
| [ket_qua/ket_qua.md](ket_qua/ket_qua.md) | Kết quả chạy lại: số liệu chính xác của Fig. 3/4 bài báo, model gốc, 12 lần train lại, phân tích |
| `ket_qua/run_train.py` | Script train 200 episode → lưu → test → vẽ biểu đồ (có seed để tái lập) |
| `ket_qua/diagnose.py` | Kiểm tra model: số nơ-ron còn sống, action chọn |
| `smart-home-energy-trading-with-DRL/` | Code gốc của tác giả, **chỉ sửa 2 dòng** `torch.load` (xem commit thứ 2) |

## Chạy nhanh

```powershell
pip install torch==2.9.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

cd smart-home-energy-trading-with-DRL
# Test model gốc của tác giả trên 2000 bước (~1 phút)
python -c "import HEMS; m=HEMS.HEMS(load=True, path='saved_nets/rtp_20_10_90_2_2'); m.test(steps=2000)"
# Train lại 1 lần (~15 phút): tên run, max_en (1 = 4 kW, 1.5 = 6 kW), seed
python ../ket_qua/run_train.py run_6kw_s2 1.5 2
```

Kết quả đúng của lệnh test: dòng cuối có `DQN cost:-89.89 | compare cost:-104.0` (± chút do agent còn 2% hành động ngẫu nhiên). Đọc số thế nào: xem [HUONG_DAN.md](HUONG_DAN.md) Phần 5, Bước 3.

**Lưu ý:** model tự train (~90 MB mỗi cái) không đưa lên repo — chạy lại `run_train.py` với cùng seed sẽ ra đúng model đó. Bài báo (PDF) không đưa lên vì bản quyền — tải qua DOI ở trên.
