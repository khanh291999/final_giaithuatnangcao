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

## Kết quả mẫu

### Thuật toán Greedy:
- Cost: 413,930
- Open primary (I): [1, 0, 1]
- Open secondary (J): [1, 1, 1, 0]

### Thuật toán MFSS:
- Cost: 407,530
- Open primary (I): [1, 0, 1]
- Open secondary (J): [0, 1, 1, 1]

## Tắt Virtual Environment

Khi hoàn tất công việc, tắt virtual environment bằng lệnh:

```bash
deactivate
```

## Cấu trúc dự án
```
.
├── greedy_tscflp.py      # Thuật toán Greedy
├── mfss_tscflp.py        # Thuật toán MFSS
├── tscflp_core.py        # Core functions
├── venv/                 # Virtual environment (tạo sau khi cài đặt)
└── README.md             # File hướng dẫn này
```

## Lưu ý
- Thư mục `venv/` không nên được commit vào Git. Thêm nó vào `.gitignore` nếu sử dụng version control.
- Chỉ cần cài đặt thư viện một lần duy nhất trong virtual environment.
- Mỗi lần mở terminal mới, cần kích hoạt lại virtual environment trước khi chạy chương trình.
