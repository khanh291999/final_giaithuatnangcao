# analyze_results.py
"""
Script đọc và phân tích file kết quả so sánh từ compare_algorithms.py
Có thể sử dụng để phân tích nhiều lần chạy hoặc tạo visualization
"""

import json
import glob
import os
from datetime import datetime


def load_latest_results():
    """Tải file kết quả mới nhất"""
    json_files = glob.glob("comparison_results_*.json")
    
    if not json_files:
        print("Không tìm thấy file kết quả nào!")
        return None
    
    # Sắp xếp theo thời gian tạo file (mới nhất trước)
    latest_file = max(json_files, key=os.path.getctime)
    
    print(f"Đang đọc file: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_results(results):
    """Phân tích và in ra thông tin chi tiết"""
    
    if not results:
        return
    
    print("\n" + "="*70)
    print("PHÂN TÍCH KẾT QUẢ SO SÁNH THUẬT TOÁN")
    print("="*70)
    
    # Thông tin instance
    print("\n📊 THÔNG TIN BÀI TOÁN:")
    info = results['instance_info']
    print(f"  • Số nhà máy (Primary):     {info['num_primary']}")
    print(f"  • Số kho (Secondary):       {info['num_secondary']}")
    print(f"  • Số khách hàng:            {info['num_customers']}")
    print(f"  • Tổng nhu cầu:             {info['total_demand']}")
    
    # Kết quả Greedy
    print("\n🔷 THUẬT TOÁN GREEDY:")
    greedy = results['algorithms']['Greedy']
    print(f"  • Chi phí:                  {greedy['cost']:,.0f}")
    print(f"  • Thời gian:                {greedy['execution_time_seconds']:.4f} giây")
    print(f"  • Nhà máy mở:               {greedy['num_open_primary']}/{info['num_primary']}")
    print(f"  • Kho mở:                   {greedy['num_open_secondary']}/{info['num_secondary']}")
    print(f"  • Pattern nhà máy:          {greedy['open_primary_facilities']}")
    print(f"  • Pattern kho:              {greedy['open_secondary_facilities']}")
    
    # Kết quả MFSS
    print("\n🔶 THUẬT TOÁN MFSS:")
    mfss = results['algorithms']['MFSS']
    print(f"  • Chi phí:                  {mfss['cost']:,.0f}")
    print(f"  • Thời gian:                {mfss['execution_time_seconds']:.4f} giây")
    print(f"  • Nhà máy mở:               {mfss['num_open_primary']}/{info['num_primary']}")
    print(f"  • Kho mở:                   {mfss['num_open_secondary']}/{info['num_secondary']}")
    print(f"  • Pattern nhà máy:          {mfss['open_primary_facilities']}")
    print(f"  • Pattern kho:              {mfss['open_secondary_facilities']}")
    
    # So sánh
    print("\n📈 SO SÁNH:")
    comp = results['comparison']
    
    if comp['cost_difference'] > 0:
        print(f"  ✓ MFSS tốt hơn Greedy")
        print(f"  • Tiết kiệm chi phí:        {comp['cost_difference']:,.0f} ({comp['cost_improvement_percentage']:.2f}%)")
    elif comp['cost_difference'] < 0:
        print(f"  ✓ Greedy tốt hơn MFSS")
        print(f"  • Tiết kiệm chi phí:        {abs(comp['cost_difference']):,.0f} ({abs(comp['cost_improvement_percentage']):.2f}%)")
    else:
        print(f"  • Cả hai thuật toán cho kết quả giống nhau")
    
    if comp['greedy_faster']:
        print(f"  • Greedy nhanh hơn:         {comp['time_difference_seconds']:.4f} giây")
        speedup = mfss['execution_time_seconds'] / greedy['execution_time_seconds']
        print(f"  • MFSS chậm hơn:            {speedup:.2f}x")
    else:
        print(f"  • MFSS nhanh hơn:           {abs(comp['time_difference_seconds']):.4f} giây")
        speedup = greedy['execution_time_seconds'] / mfss['execution_time_seconds']
        print(f"  • MFSS nhanh hơn:           {speedup:.2f}x")
    
    # Trade-off analysis
    print("\n⚖️  PHÂN TÍCH TRADE-OFF:")
    cost_saving_per_second = comp['cost_difference'] / comp['time_difference_seconds'] if comp['time_difference_seconds'] != 0 else 0
    
    if cost_saving_per_second > 0:
        print(f"  • Tiết kiệm/giây:           {cost_saving_per_second:,.2f} đơn vị chi phí")
        print(f"  • Đánh giá:                 Đáng để đợi thêm {comp['time_difference_seconds']:.2f}s")
        print(f"                              để tiết kiệm {comp['cost_improvement_percentage']:.2f}% chi phí")
    else:
        print(f"  • Greedy là lựa chọn tốt:   Nhanh hơn và chi phí tương đương")
    
    # Khác biệt về cấu trúc lời giải
    print("\n🔍 KHÁC BIỆT CẤU TRÚC:")
    primary_diff = sum(1 for i in range(info['num_primary']) 
                      if greedy['open_primary_facilities'][i] != mfss['open_primary_facilities'][i])
    secondary_diff = sum(1 for j in range(info['num_secondary']) 
                        if greedy['open_secondary_facilities'][j] != mfss['open_secondary_facilities'][j])
    
    print(f"  • Nhà máy khác nhau:        {primary_diff}/{info['num_primary']}")
    print(f"  • Kho khác nhau:            {secondary_diff}/{info['num_secondary']}")
    
    if primary_diff == 0 and secondary_diff == 0:
        print(f"  • Kết luận:                 Cùng cấu trúc facility, khác về luồng phân phối")
    else:
        print(f"  • Kết luận:                 Hai lời giải có cấu trúc khác nhau")
    
    print("\n" + "="*70 + "\n")


def compare_multiple_runs():
    """So sánh nhiều lần chạy (nếu có)"""
    json_files = glob.glob("comparison_results_*.json")
    
    if len(json_files) < 2:
        print("Cần ít nhất 2 file kết quả để so sánh nhiều lần chạy")
        return
    
    print("\n" + "="*70)
    print(f"PHÂN TÍCH {len(json_files)} LẦN CHẠY")
    print("="*70 + "\n")
    
    greedy_costs = []
    mfss_costs = []
    improvements = []
    
    for file in sorted(json_files):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            greedy_costs.append(data['algorithms']['Greedy']['cost'])
            mfss_costs.append(data['algorithms']['MFSS']['cost'])
            improvements.append(data['comparison']['cost_improvement_percentage'])
        print(f"✓ {file}")
    
    print(f"\n📊 THỐNG KÊ:")
    print(f"  Greedy - Trung bình: {sum(greedy_costs)/len(greedy_costs):,.0f}")
    print(f"  Greedy - Tốt nhất:   {min(greedy_costs):,.0f}")
    print(f"  Greedy - Tệ nhất:    {max(greedy_costs):,.0f}")
    
    print(f"\n  MFSS - Trung bình:   {sum(mfss_costs)/len(mfss_costs):,.0f}")
    print(f"  MFSS - Tốt nhất:     {min(mfss_costs):,.0f}")
    print(f"  MFSS - Tệ nhất:      {max(mfss_costs):,.0f}")
    
    print(f"\n  Cải thiện trung bình: {sum(improvements)/len(improvements):.2f}%")
    print(f"  Cải thiện tốt nhất:   {max(improvements):.2f}%")
    print(f"  Cải thiện tệ nhất:    {min(improvements):.2f}%")
    print()


if __name__ == "__main__":
    # Phân tích file kết quả mới nhất
    results = load_latest_results()
    analyze_results(results)
    
    # Nếu có nhiều file, phân tích tất cả
    # compare_multiple_runs()

