# tscflp_core.py
"""
File lõi dùng chung cho cả Greedy và MFSS.

- Định nghĩa cấu trúc dữ liệu cho bài toán TSCFLP
- Cài đặt hàm solve_full_mip() dùng PuLP để giải MILP
- Có thêm hàm build_vietnam_example() với dữ liệu "thật" mô phỏng TP.HCM
- Hàm build_small_example() chỉ là alias gọi sang build_vietnam_example()
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import pulp as pl


# =====================================================================
# 1. ĐỊNH NGHĨA INSTANCE BÀI TOÁN & CẤU TRÚC LƯU LỜI GIẢI
# =====================================================================

@dataclass
class TSCFLPInstance:
    """
    Mô tả 1 instance của bài toán Two-Stage Capacitated Facility Location Problem (TSCFLP)

    Tầng 1: primary facilities (nhà máy)       i ∈ I
    Tầng 2: secondary facilities (kho)         j ∈ J
    Khách hàng                                 k ∈ K

    Mục tiêu: mở một số nhà máy + kho, và quyết định luồng hàng w(i,j), z(j,k)
               sao cho tổng:
                    - chi phí mở nhà máy
                    - chi phí mở kho
                    - chi phí vận chuyển i->j
                    - chi phí vận chuyển j->k
               là nhỏ nhất, đồng thời thỏa:
                    - capacity của nhà máy, kho
                    - thỏa mãn demand khách hàng
    """
    # primary facilities (nhà máy)
    f: List[float]     # fixed cost mở tại i
    U: List[float]     # capacity (công suất tối đa) tại i

    # secondary facilities (kho)
    g: List[float]     # fixed cost mở tại j
    V: List[float]     # capacity tại j

    # customers
    D: List[float]     # nhu cầu của khách hàng k

    # transport costs
    c: List[List[float]]  # chi phí đơn vị i -> j
    d: List[List[float]]  # chi phí đơn vị j -> k

    def __post_init__(self):
        """
        Sau khi khởi tạo, tạo luôn các tập chỉ số I, J, K
        để dùng cho vòng lặp cho tiện.
        """
        self.I = list(range(len(self.f)))   # index nhà máy
        self.J = list(range(len(self.g)))   # index kho
        self.K = list(range(len(self.D)))   # index khách hàng


@dataclass
class Solution:
    """
    Lưu lời giải ở mức "facility mở hay không" + cost.
    (Phần luồng chi tiết w(i,j), z(j,k) không lưu lại ở đây
     vì mục đích chính là so sánh cost và pattern mở/đóng.)
    """
    cost: float
    open_I: List[int]   # 0/1 cho từng nhà máy i
    open_J: List[int]   # 0/1 cho từng kho j


# =====================================================================
# 2. HÀM GIẢI MILP ĐẦY ĐỦ CHO TSCFLP (DÙNG CHUNG CHO GREEDY + MFSS)
# =====================================================================

def solve_full_mip(inst: TSCFLPInstance,
                   time_limit: Optional[float] = None,
                   fixed: Optional[Dict[str, Dict[int, int]]] = None
                   ) -> Solution:
    """
    Giải đầy đủ mô hình MILP của TSCFLP bằng PuLP (CBC).

    Parameters
    ----------
    inst : TSCFLPInstance
        Instance của bài toán.
    time_limit : float, optional
        Giới hạn thời gian cho solver (giây). Nếu None thì không giới hạn.
    fixed : dict, optional
        Nếu muốn "cố định" một số biến x_i, y_j (dùng trong MFSS),
        truyền vào dạng:
            {
              'I': {i: 0 hoặc 1, ...},
              'J': {j: 0 hoặc 1, ...}
            }

    Returns
    -------
    Solution
        Cost tối ưu (hoặc tốt nhất trong time limit) và pattern mở/đóng facility.
    """
    I, J, K = inst.I, inst.J, inst.K
    f, g, U, V, D = inst.f, inst.g, inst.U, inst.V, inst.D
    c, d = inst.c, inst.d

    # Tạo model tối thiểu hóa
    prob = pl.LpProblem("TSCFLP", pl.LpMinimize)

    # Biến nhị phân: x_i = 1 nếu mở nhà máy i
    x = pl.LpVariable.dicts("x", I, lowBound=0, upBound=1, cat="Binary")
    # Biến nhị phân: y_j = 1 nếu mở kho j
    y = pl.LpVariable.dicts("y", J, lowBound=0, upBound=1, cat="Binary")

    # Biến luồng: w_ij = lượng hàng từ nhà máy i -> kho j
    w = pl.LpVariable.dicts("w", (I, J), lowBound=0, cat="Continuous")
    # Biến luồng: z_jk = lượng hàng từ kho j -> khách k
    z = pl.LpVariable.dicts("z", (J, K), lowBound=0, cat="Continuous")

    # --------- Objective: (1) trong bài báo ---------
    prob += (
        pl.lpSum(f[i] * x[i] for i in I) +                     # chi phí mở nhà máy
        pl.lpSum(g[j] * y[j] for j in J) +                     # chi phí mở kho
        pl.lpSum(c[i][j] * w[i][j] for i in I for j in J) +    # chi phí vận chuyển i->j
        pl.lpSum(d[j][k] * z[j][k] for j in J for k in K)      # chi phí vận chuyển j->k
    )

    # --------- Ràng buộc capacity nhà máy: (2) ---------
    for i in I:
        prob += pl.lpSum(w[i][j] for j in J) <= U[i] * x[i]

    # --------- Ràng buộc capacity kho: (3) ---------
    for j in J:
        prob += pl.lpSum(z[j][k] for k in K) <= V[j] * y[j]

    # --------- Bảo toàn luồng qua kho: (4) ---------
    for j in J:
        prob += pl.lpSum(w[i][j] for i in I) == pl.lpSum(z[j][k] for k in K)

    # --------- Thỏa nhu cầu khách hàng: (5) ---------
    for k in K:
        prob += pl.lpSum(z[j][k] for j in J) == D[k]

    # --------- Nếu có fixed-set: thêm ràng buộc x_i / y_j = 0/1 ---------
    if fixed is not None:
        # fixed['I'] chứa list i phải fix
        for i, val in fixed.get('I', {}).items():
            prob += x[i] == int(val)
        # fixed['J'] chứa list j phải fix
        for j, val in fixed.get('J', {}).items():
            prob += y[j] == int(val)

    # Chọn solver CBC (mặc định của PuLP) + giới hạn thời gian
    solver = pl.PULP_CBC_CMD(msg=True, timeLimit=time_limit)
    prob.solve(solver)

    cost = pl.value(prob.objective)
    open_I = [int(round(x[i].value())) for i in I]
    open_J = [int(round(y[j].value())) for j in J]

    return Solution(cost=cost, open_I=open_I, open_J=open_J)


# =====================================================================
# 3. DỮ LIỆU "THẬT" GIẢ LẬP LOGISTICS TP.HCM
# =====================================================================

def build_vietnam_example() -> TSCFLPInstance:
    """
    Ví dụ mô phỏng mạng lưới phân phối quanh TP.HCM.

    Primary (nhà máy):
        0: Bình Dương
        1: Long An
        2: Đồng Nai

    Secondary (kho):
        0: Kho Thủ Đức
        1: Kho Tân Bình
        2: Kho Bình Tân
        3: Kho Hóc Môn

    Customers (nhu cầu theo khu):
        0: Quận 1
        1: Gò Vấp
        2: TP. Thủ Đức
        3: Quận Bình Tân
        4: Nhà Bè
        5: Củ Chi
    """

    # ---- Chi phí mở + capacity nhà máy (primary) ----
    # Đơn vị: cost mở cơ sở (có thể hiểu là ngàn / triệu đồng)
    # Capacity: số pallet / đơn vị thời gian (tháng, tuần, ...)
    f = [
        120000,  # Bình Dương
        115000,  # Long An
        110000   # Đồng Nai
    ]

    U = [
        300,  # Bình Dương
        250,  # Long An
        250   # Đồng Nai
    ]

    # ---- Chi phí mở + capacity kho (secondary) ----
    g = [
        60000,  # Kho Thủ Đức
        58000,  # Kho Tân Bình
        55000,  # Kho Bình Tân
        53000   # Kho Hóc Môn
    ]

    V = [
        220,  # Thủ Đức
        210,  # Tân Bình
        200,  # Bình Tân
        180   # Hóc Môn
    ]

    # ---- Nhu cầu khách hàng (tổng ≈ 520, nhỏ hơn tổng capacity) ----
    D = [
        90,   # Quận 1
        110,  # Gò Vấp
        100,  # TP. Thủ Đức
        90,   # Quận Bình Tân
        70,   # Nhà Bè
        60    # Củ Chi
    ]

    # ---- Chi phí vận chuyển i -> j (nhà máy -> kho) ----
    # Đơn vị: chi phí / pallet. Giả lập dựa trên cảm giác khoảng cách:
    #  - Bình Dương -> Thủ Đức rẻ (gần), xa hơn thì đắt hơn chút
    #  - Long An gần Bình Tân / Nhà Bè hơn
    #  - Đồng Nai gần Thủ Đức / phía Đông thành phố
    c = [
        # Kho:   Thủ Đức, Tân Bình, Bình Tân, Hóc Môn
        [10,       14,      16,      15],   # Nhà máy Bình Dương
        [16,       12,      10,      17],   # Nhà máy Long An
        [11,       15,      18,      14]    # Nhà máy Đồng Nai
    ]

    # ---- Chi phí vận chuyển j -> k (kho -> khách) ----
    # Mỗi dòng là 1 kho, mỗi cột là 1 khu khách hàng.
    # cost thấp khi kho gần khu đó, cao khi xa.
    d = [
        # Khách:  Q1,  Gò Vấp, Thủ Đức, Bình Tân, Nhà Bè, Củ Chi
        [   8,      9,      5,      11,      12,     15],  # Kho Thủ Đức
        [   6,      8,     10,       7,      11,     13],  # Kho Tân Bình
        [   7,      9,     12,       6,      10,     14],  # Kho Bình Tân
        [  10,      7,     11,       8,      13,      6],  # Kho Hóc Môn
    ]

    return TSCFLPInstance(f=f, U=U, g=g, V=V, D=D, c=c, d=d)


def build_small_example() -> TSCFLPInstance:
    """
    Giữ tên hàm cũ để các file khác (greedy_tscflp.py, mfss_tscflp.py) dùng lại,
    nhưng bên trong ta trả về ví dụ "thật" ở trên.

    Nếu sau này bạn muốn thêm nhiều dataset khác (ví dụ miền Bắc),
    có thể tạo hàm build_vietnam_north_example() rồi cho build_small_example()
    chọn dataset theo tham số / biến môi trường.
    """
    return build_vietnam_example()
