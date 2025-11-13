# greedy_tscflp.py
"""
Cài đặt Algorithm 1: Greedy Algorithm for the TSCFLP.

- Sinh 1 lời giải khả thi bằng cách:
  + chọn dần các primary (nhà máy) theo heuristic h_p(i, S)
  + với mỗi primary, chọn các secondary (kho) theo h_s(i, j, S)
  + với mỗi secondary, gán cho các khách có chi phí d_jk nhỏ nhất
- Sau khi đã chọn tập facility, gọi lại MILP để tối ưu luồng (SolveMinCostFlow)
"""

import random
from typing import List, Tuple
import numpy as np

from tscflp_core import TSCFLPInstance, Solution, solve_full_mip, build_small_example


def greedy_tscflp(inst: TSCFLPInstance, rcl_size: int = 1) -> Solution:
    """
    Cài đặt gần sát Algorithm 1 trong paper.

    Parameters
    ----------
    inst : TSCFLPInstance
        Instance bài toán.
    rcl_size : int
        - Nếu rcl_size = 1  -> thuần greedy (luôn chọn ứng viên tốt nhất).
        - Nếu rcl_size > 1  -> dùng RCL (Restricted Candidate List):
                              chọn ngẫu nhiên trong top rcl_size ứng viên tốt nhất.
                              Dùng khi cần randomization để sinh nhiều lời giải khác nhau
                              (ví dụ dùng cho population khởi tạo của MFSS).

    Returns
    -------
    Solution
        Lời giải (pattern facility mở + cost) sau khi giải lại MILP để tối ưu luồng.
    """
    I, J, K = inst.I, inst.J, inst.K
    f, g, U0, V0, D0 = inst.f, inst.g, inst.U, inst.V, inst.D
    c, d = inst.c, inst.d

    # Copy capacity/demand vì chúng ta sẽ giảm dần trong quá trình xây dựng lời giải
    U = U0.copy()   # capacity còn lại của nhà máy
    V = V0.copy()   # capacity còn lại của kho
    D = D0.copy()   # demand còn lại của khách

    total_demand = sum(D)

    selected_I = set()  # nhà máy được chọn
    selected_J = set()  # kho được chọn

    # Tập khách hàng chưa được đáp ứng hoàn toàn
    unmet_customers = set(k for k in K if D[k] > 0)

    def choose_with_rcl(scores: List[Tuple[int, float]], rcl_sz: int):
        """
        scores: list[(index, heuristic_value)].
        Sắp xếp tăng dần theo heuristic_value,
        lấy top rcl_sz phần tử tốt nhất, rồi chọn ngẫu nhiên 1 phần tử trong đó.
        """
        scores = sorted(scores, key=lambda x: x[1])
        rcl = scores[:max(1, min(rcl_sz, len(scores)))]
        return random.choice(rcl)[0]

    # ----------------- Vòng lặp chính: while T > 0 trong Algorithm 1 -----------------
    while total_demand > 1e-6:
        # ======== 1) Chọn primary facility i (dòng 4 trong pseudocode) ========
        cand_I = [i for i in I if U[i] > 1e-6]   # chỉ xét những nhà máy còn capacity
        if not cand_I:
            raise RuntimeError("Không đủ capacity primary để đáp ứng demand")

        # J_available: những kho còn capacity, dùng để tính avg cost trong h_p
        J_available = [j for j in J if V[j] > 1e-6]

        scores_i = []
        for i in cand_I:
            # hp(i, S) = f_i / U_i + average(chi phí i -> các kho còn dùng được)
            avg_c = np.mean([c[i][j] for j in J_available]) if J_available else 0.0
            hp = f[i] / (U0[i] + 1e-9) + avg_c
            scores_i.append((i, hp))

        i_star = choose_with_rcl(scores_i, rcl_size)
        selected_I.add(i_star)

        # U_used = lượng capacity của i_star dùng để đáp ứng một phần tổng demand T
        U_used = min(total_demand, U[i_star])
        U[i_star] -= U_used
        remaining_from_i = U_used
        total_demand -= U_used

        # ======== 2) Chọn lần lượt các secondary facility j (dòng 10) ========
        while remaining_from_i > 1e-6:
            cand_J = [j for j in J if V[j] > 1e-6]
            if not cand_J:
                raise RuntimeError("Không đủ capacity secondary để nhận hàng")

            scores_j = []
            for j in cand_J:
                # hs(i,j,S) = c_ij + g_j / V_j + avg(d_jk) với các khách chưa được phục vụ
                avg_d = np.mean([d[j][k] for k in unmet_customers]) if unmet_customers else 0.0
                hs = c[i_star][j] + g[j] / (V0[j] + 1e-9) + avg_d
                scores_j.append((j, hs))

            j_star = choose_with_rcl(scores_j, rcl_size)
            selected_J.add(j_star)

            # V_used = lượng hàng từ i_star chuyển sang kho j_star (không quá capacity V[j_star])
            V_used = min(remaining_from_i, V[j_star])
            V[j_star] -= V_used
            remaining_from_i -= V_used

            remaining_from_j = V_used

            # ======== 3) Gán hàng từ kho j_star cho các khách k (dòng 15) ========
            while remaining_from_j > 1e-6:
                # chỉ xem các khách còn nhu cầu
                cand_K = [k for k in unmet_customers if D[k] > 1e-6]
                if not cand_K:
                    break

                # hc(j,k) = d_jk (chi phí vận chuyển kho -> khách)
                scores_k = [(k, d[j_star][k]) for k in cand_K]
                k_star = choose_with_rcl(scores_k, rcl_size)

                # lượng giao cho khách k_star
                amount = min(remaining_from_j, D[k_star])
                D[k_star] -= amount
                remaining_from_j -= amount

                if D[k_star] <= 1e-6 and k_star in unmet_customers:
                    unmet_customers.remove(k_star)

    # ----------------- Bước cuối: SolveMinCostFlow(S) -----------------
    # Sau khi quyết định tập facility mở/đóng, ta giải lại MILP để tìm luồng tối ưu
    fixed = {
        'I': {i: (1 if i in selected_I else 0) for i in I},
        'J': {j: (1 if j in selected_J else 0) for j in J},
    }
    sol = solve_full_mip(inst, fixed=fixed)
    return sol


if __name__ == "__main__":
    # Demo chạy riêng thuật toán Greedy
    random.seed(0)  # để kết quả lặp lại được
    inst = build_small_example()

    print("=== CHẠY GREEDY (Algorithm 1) ===")
    sol = greedy_tscflp(inst, rcl_size=1)  # pure greedy
    print("Cost:", sol.cost)
    print("Open primary (I):", sol.open_I)
    print("Open secondary (J):", sol.open_J)
