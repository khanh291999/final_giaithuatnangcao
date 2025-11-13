# mfss_tscflp.py
"""
Cài đặt Algorithm 2: Matheuristic Fixed Set Search (MFSS) cho TSCFLP.

Luồng chính:
- Khởi tạo population P bằng randomized greedy (Algorithm 1 với RCL > 1).
- Mỗi vòng:
  + Lấy tập Sn gồm n_best lời giải tốt nhất.
  + Chọn ngẫu nhiên 1 base solution B trong Sn.
  + Chọn k lời giải từ Sn tạo thành Skn.
  + Xây fixed set F (những biến x_i, y_j sẽ bị fix 0/1).
  + Gọi solver MILP với fixed-set F để tìm lời giải mới S_new.
  + Nếu S_new tốt hơn best hiện tại và chưa trùng pattern -> thêm vào P.
  + Nếu bị "kẹt" nhiều vòng không cải thiện -> tăng time limit.
"""

import random
from typing import List

from tscflp_core import TSCFLPInstance, Solution, solve_full_mip, build_small_example
from greedy_tscflp import greedy_tscflp


def build_fixed_set(base: Solution,
                    Skn: List[Solution],
                    Size: int,
                    inst: TSCFLPInstance):
    """
    Xây fixed set F giống ý tưởng trong bài:

    - Với mỗi facility:
        + nếu là primary: xem trạng thái open_I[i] của base
        + nếu là secondary: xem trạng thái open_J[j] của base
      rồi đếm trong Skn có bao nhiêu lời giải có cùng trạng thái đó.

    - Những facility có "tần suất xuất hiện giống base" cao nhất sẽ được đưa vào F
      và bị fix = trạng thái trong base.

    Điều này phản ánh ý tưởng:
      "những pattern hay xuất hiện trong nhiều lời giải tốt thì có khả năng là 'tốt',
       nên ta giữ cố định chúng và chỉ tối ưu phần còn lại."
    """
    I, J = inst.I, inst.J

    scores = []  # mỗi phần tử: (score, ('I', i) or ('J', j))

    # Đánh điểm cho các nhà máy
    for i in I:
        cnt = sum(1 for S in Skn if S.open_I[i] == base.open_I[i])
        scores.append((cnt, ('I', i)))

    # Đánh điểm cho các kho
    for j in J:
        cnt = sum(1 for S in Skn if S.open_J[j] == base.open_J[j])
        scores.append((cnt, ('J', j)))

    # Sắp xếp giảm dần theo score (tần suất)
    scores.sort(key=lambda x: x[0], reverse=True)

    if Size >= len(scores):
        # Nếu Size lớn hơn số facility, fix hết
        chosen = scores
    else:
        # Nếu không thì chọn Size phần tử,
        # nhưng xử lý tie giống trong paper:
        cutoff = scores[Size - 1][0]
        # những phần tử có score > cutoff thì luôn được chọn
        prefix = [s for s in scores if s[0] > cutoff]
        # những phần tử score = cutoff cho vào "group tie"
        tied = [s for s in scores if s[0] == cutoff]
        needed = Size - len(prefix)
        # random lấy "needed" phần tử trong group tie
        chosen = prefix + random.sample(tied, needed)

    # Chuyển thành dict fixed-set cho solver
    fixed_I = {}
    fixed_J = {}
    for _, (typ, idx) in chosen:
        if typ == 'I':
            fixed_I[idx] = base.open_I[idx]
        else:
            fixed_J[idx] = base.open_J[idx]

    return {'I': fixed_I, 'J': fixed_J}


def mfss(inst: TSCFLPInstance,
         Npop: int = 10,
         n_best: int = 5,
         Sizemax: int = 10,
         tinit: float = 1.0,
         max_iter: int = 50) -> Solution:
    """
    Cài đặt MFSS (phiên bản đơn giản hóa so với paper, nhưng cùng ý tưởng).

    Parameters
    ----------
    inst : TSCFLPInstance
        Instance bài toán.
    Npop : int
        Kích thước population ban đầu (số lời giải từ Greedy random).
    n_best : int
        Số lời giải tốt nhất dùng để tạo Sn (top-n).
    Sizemax : int
        Số lượng biến (facility) tối đa được "thả tự do" trong subproblem.
        => fixed-set sẽ có khoảng (|I| + |J| - Sizemax) biến được fix.
    tinit : float
        Time limit ban đầu cho solver MILP (giây).
    max_iter : int
        Số vòng lặp MFSS.

    Returns
    -------
    Solution
        Lời giải tốt nhất tìm được trong quá trình MFSS.
    """
    random.seed(0)

    # ---------- 1) Khởi tạo population P bằng randomized greedy ----------
    P: List[Solution] = []
    for _ in range(Npop):
        # RCL size = 2 => tạo ra nhiều lời giải khác nhau
        sol = greedy_tscflp(inst, rcl_size=2)
        P.append(sol)

    # tau = time limit hiện tại cho MILP
    tau = tinit
    # Số facility total
    total_fac = len(inst.I) + len(inst.J)
    # Số biến sẽ bị fix = total_fac - Sizemax
    Size = min(total_fac - 1, total_fac - Sizemax)  # bảo đảm dương

    # Lời giải tốt nhất hiện tại
    best_sol = min(P, key=lambda s: s.cost)
    stag = 0  # đếm số vòng không cải thiện (stagnation)

    # ---------- 2) Vòng lặp học Fixed Set Search ----------
    for it in range(max_iter):
        # Sắp xếp P theo cost tăng dần, lấy top n_best
        P.sort(key=lambda s: s.cost)
        Sn = P[:min(n_best, len(P))]

        # Chọn base solution B ngẫu nhiên trong top-n
        B = random.choice(Sn)

        # Chọn k lời giải từ Sn để tạo Skn (k ngẫu nhiên)
        k = random.randint(2, max(2, len(Sn)))
        Skn = random.sample(Sn, k=k)

        # Xây fixed set F dựa trên B và Skn
        F = build_fixed_set(B, Skn, Size, inst)

        # Giải MILP với fixed-set F, time limit = tau
        S_new = solve_full_mip(inst, time_limit=tau, fixed=F)

        # Hàm so sánh pattern (facility mở/đóng) giữa 2 lời giải
        def same_pattern(a: Solution, b: Solution) -> bool:
            return a.open_I == b.open_I and a.open_J == b.open_J

        # Kiểm tra xem S_new đã tồn tại trong P chưa
        exists = any(same_pattern(S_new, s) for s in P)

        # Nếu mới + tốt hơn best_sol thì update
        if (not exists) and (S_new.cost < best_sol.cost - 1e-6):
            P.append(S_new)
            best_sol = S_new
            stag = 0
            print(f"[Iter {it}] Improved solution: cost = {best_sol.cost:.4f}")
        else:
            stag += 1

        # Nếu 5 vòng không cải thiện: tăng time limit lên 2x
        # (gần giống ý tưởng paper tăng τ khi bị stagnation)
        if stag >= 5:
            tau *= 2
            stag = 0
            print(f"[Iter {it}] No improvement, tăng time limit lên {tau} s")

    return best_sol


if __name__ == "__main__":
    # Demo chạy MFSS trên instance nhỏ
    inst = build_small_example()

    print("=== CHẠY MFSS (Algorithm 2) ===")
    sol = mfss(inst,
               Npop=10,
               n_best=5,
               Sizemax=5,   # subproblem cho phép khoảng 5 facility được tự do
               tinit=1.0,
               max_iter=20)
    print("Cost MFSS:", sol.cost)
    print("Open primary (I):", sol.open_I)
    print("Open secondary (J):", sol.open_J)
