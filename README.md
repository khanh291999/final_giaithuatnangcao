# TSCFLP - Two-Stage Capacitated Facility Location Problem

## Mô tả
Dự án này triển khai hai thuật toán để giải quyết bài toán Two-Stage Capacitated Facility Location Problem (TSCFLP):
- **Algorithm 1**: Thuật toán Greedy
- **Algorithm 2**: Thuật toán MFSS (Multi-Facility Subset Selection)

## Yêu cầu hệ thống
- Python 3.x
- pip (Python package installer)

## Cài đặt

### 1. Tạo Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
```

**Linux/MacOS:**
```bash
python3 -m venv venv
```

### 2. Kích hoạt Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/MacOS:**
```bash
source venv/bin/activate
```

### 3. Cài đặt thư viện cần thiết

Sau khi kích hoạt virtual environment, cài đặt các thư viện:

```bash
pip install pulp numpy
```

## Cách chạy chương trình

Đảm bảo virtual environment đã được kích hoạt (bạn sẽ thấy `(venv)` ở đầu dòng lệnh).

### Chạy thuật toán Greedy (Algorithm 1):
```bash
python greedy_tscflp.py
```

### Chạy thuật toán MFSS (Algorithm 2):
```bash
python mfss_tscflp.py
```

### So sánh cả hai thuật toán và xuất kết quả:
```bash
python compare_algorithms.py
```

Script này sẽ:
- Chạy cả hai thuật toán trên cùng instance
- Tạo 3 file output với timestamp:
  - `comparison_results_YYYYMMDD_HHMMSS.json` - Kết quả dạng JSON
  - `comparison_results_YYYYMMDD_HHMMSS.csv` - Kết quả dạng bảng CSV
  - `detailed_comparison_YYYYMMDD_HHMMSS.txt` - Báo cáo chi tiết dạng text

### Phân tích kết quả so sánh:
```bash
python analyze_results.py
```

Script này sẽ:
- Tự động đọc file kết quả mới nhất
- Hiển thị phân tích chi tiết về:
  - Thông tin bài toán
  - Kết quả từng thuật toán
  - So sánh chi phí và thời gian
  - Trade-off analysis (đánh giá đáng đợi hay không)
  - Khác biệt về cấu trúc lời giải

## Kết quả mẫu

### Chạy riêng lẻ:

**Thuật toán Greedy:**
```
Cost: 413,930
Open primary (I): [1, 0, 1]
Open secondary (J): [1, 1, 1, 0]
Execution time: ~0.04 seconds
```

**Thuật toán MFSS:**
```
Cost: 407,530
Open primary (I): [1, 0, 1]
Open secondary (J): [0, 1, 1, 1]
Execution time: ~1.87 seconds
```

### So sánh (từ analyze_results.py):

```
📈 SO SÁNH:
  ✓ MFSS tốt hơn Greedy
  • Tiết kiệm chi phí:        6,400 (1.55%)
  • Greedy nhanh hơn:         1.83 giây
  • MFSS chậm hơn:            42.88x

⚖️  PHÂN TÍCH TRADE-OFF:
  • Tiết kiệm/giây:           3,504.93 đơn vị chi phí
  • Đánh giá:                 Đáng để đợi thêm 1.83s
                              để tiết kiệm 1.55% chi phí

🔍 KHÁC BIỆT CẤU TRÚC:
  • Nhà máy khác nhau:        0/3
  • Kho khác nhau:            2/4
  • Kết luận:                 Hai lời giải có cấu trúc khác nhau
```

## Tắt Virtual Environment

Khi hoàn tất công việc, tắt virtual environment bằng lệnh:

```bash
deactivate
```

## Cấu trúc dự án
```
.
├── greedy_tscflp.py                # Thuật toán Greedy
├── mfss_tscflp.py                  # Thuật toán MFSS
├── tscflp_core.py                  # Core functions
├── compare_algorithms.py           # Script so sánh hai thuật toán
├── analyze_results.py              # Script phân tích kết quả
├── venv/                           # Virtual environment (tạo sau khi cài đặt)
├── .gitignore                      # Git ignore file
├── README.md                       # File hướng dẫn này
└── comparison_results_*.json/csv/txt  # File kết quả so sánh (tạo khi chạy compare_algorithms.py)
```

## Metrics so sánh

Khi chạy `compare_algorithms.py`, bạn sẽ nhận được các metrics sau:

### JSON Output
- **timestamp**: Thời gian chạy
- **instance_info**: Thông tin về bài toán (số lượng facilities, customers, demand)
- **algorithms**: Kết quả chi tiết của từng thuật toán
  - cost: Chi phí tổng
  - execution_time_seconds: Thời gian thực thi
  - open_primary_facilities: Danh sách nhà máy mở
  - open_secondary_facilities: Danh sách kho mở
  - num_open_primary: Số lượng nhà máy mở
  - num_open_secondary: Số lượng kho mở
- **comparison**: So sánh giữa hai thuật toán
  - cost_difference: Chênh lệch chi phí
  - cost_improvement_percentage: Phần trăm cải thiện
  - better_algorithm: Thuật toán tốt hơn
  - time_difference_seconds: Chênh lệch thời gian

### CSV Output
Bảng so sánh dễ đọc với các cột: Metric, Greedy, MFSS, Difference/Better

### Text Report
Báo cáo chi tiết dạng văn bản với đầy đủ thông tin

## Lưu ý
- Thư mục `venv/` không nên được commit vào Git. Thêm nó vào `.gitignore` nếu sử dụng version control.
- Chỉ cần cài đặt thư viện một lần duy nhất trong virtual environment.
- Mỗi lần mở terminal mới, cần kích hoạt lại virtual environment trước khi chạy chương trình.
