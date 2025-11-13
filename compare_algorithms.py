# compare_algorithms.py
"""
Script so sánh hiệu suất giữa Algorithm 1 (Greedy) và Algorithm 2 (MFSS).
Xuất kết quả ra file JSON và CSV để dễ dàng phân tích.
"""

import json
import csv
import time
from datetime import datetime
from tscflp_core import build_small_example
from greedy_tscflp import greedy_tscflp
from mfss_tscflp import mfss


def run_comparison():
    """Chạy cả hai thuật toán và thu thập metrics"""
    
    # Tạo instance
    inst = build_small_example()
    
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "instance_info": {
            "num_primary": len(inst.I),
            "num_secondary": len(inst.J),
            "num_customers": len(inst.K),
            "total_demand": sum(inst.D)
        },
        "algorithms": {}
    }
    
    # ==================== GREEDY ALGORITHM ====================
    print("="*60)
    print("Running GREEDY Algorithm (Algorithm 1)...")
    print("="*60)
    
    start_time = time.time()
    greedy_sol = greedy_tscflp(inst, rcl_size=1)
    greedy_time = time.time() - start_time
    
    results["algorithms"]["Greedy"] = {
        "cost": greedy_sol.cost,
        "execution_time_seconds": round(greedy_time, 4),
        "open_primary_facilities": greedy_sol.open_I,
        "open_secondary_facilities": greedy_sol.open_J,
        "num_open_primary": sum(greedy_sol.open_I),
        "num_open_secondary": sum(greedy_sol.open_J),
        "total_facilities_opened": sum(greedy_sol.open_I) + sum(greedy_sol.open_J)
    }
    
    print(f"✓ Greedy completed in {greedy_time:.4f} seconds")
    print(f"  Cost: {greedy_sol.cost}")
    print(f"  Open Primary: {greedy_sol.open_I}")
    print(f"  Open Secondary: {greedy_sol.open_J}")
    print()
    
    # ==================== MFSS ALGORITHM ====================
    print("="*60)
    print("Running MFSS Algorithm (Algorithm 2)...")
    print("="*60)
    
    start_time = time.time()
    mfss_sol = mfss(
        inst,
        Npop=10,
        n_best=5,
        Sizemax=5,
        tinit=1.0,
        max_iter=20
    )
    mfss_time = time.time() - start_time
    
    results["algorithms"]["MFSS"] = {
        "cost": mfss_sol.cost,
        "execution_time_seconds": round(mfss_time, 4),
        "open_primary_facilities": mfss_sol.open_I,
        "open_secondary_facilities": mfss_sol.open_J,
        "num_open_primary": sum(mfss_sol.open_I),
        "num_open_secondary": sum(mfss_sol.open_J),
        "total_facilities_opened": sum(mfss_sol.open_I) + sum(mfss_sol.open_J)
    }
    
    print(f"✓ MFSS completed in {mfss_time:.4f} seconds")
    print(f"  Cost: {mfss_sol.cost}")
    print(f"  Open Primary: {mfss_sol.open_I}")
    print(f"  Open Secondary: {mfss_sol.open_J}")
    print()
    
    # ==================== COMPARISON METRICS ====================
    cost_diff = greedy_sol.cost - mfss_sol.cost
    cost_improvement_pct = (cost_diff / greedy_sol.cost) * 100 if greedy_sol.cost > 0 else 0
    
    results["comparison"] = {
        "cost_difference": round(cost_diff, 2),
        "cost_improvement_percentage": round(cost_improvement_pct, 2),
        "better_algorithm": "MFSS" if mfss_sol.cost < greedy_sol.cost else "Greedy",
        "time_difference_seconds": round(mfss_time - greedy_time, 4),
        "greedy_faster": greedy_time < mfss_time
    }
    
    return results


def save_results(results):
    """Lưu kết quả ra file JSON và CSV"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # ==================== SAVE JSON ====================
    json_filename = f"comparison_results_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(results, indent=4, fp=f)
    print(f"✓ JSON results saved to: {json_filename}")
    
    # ==================== SAVE CSV ====================
    csv_filename = f"comparison_results_{timestamp}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Metric', 'Greedy', 'MFSS', 'Difference/Better'])
        
        # Rows
        greedy = results["algorithms"]["Greedy"]
        mfss = results["algorithms"]["MFSS"]
        comp = results["comparison"]
        
        writer.writerow(['Cost', greedy["cost"], mfss["cost"], comp["cost_difference"]])
        writer.writerow(['Execution Time (s)', greedy["execution_time_seconds"], 
                        mfss["execution_time_seconds"], comp["time_difference_seconds"]])
        writer.writerow(['Open Primary Facilities', greedy["num_open_primary"], 
                        mfss["num_open_primary"], ''])
        writer.writerow(['Open Secondary Facilities', greedy["num_open_secondary"], 
                        mfss["num_open_secondary"], ''])
        writer.writerow(['Total Facilities Opened', greedy["total_facilities_opened"], 
                        mfss["total_facilities_opened"], ''])
        writer.writerow(['Cost Improvement (%)', '', '', comp["cost_improvement_percentage"]])
        writer.writerow(['Better Algorithm', '', '', comp["better_algorithm"]])
        
    print(f"✓ CSV results saved to: {csv_filename}")
    
    # ==================== SAVE DETAILED COMPARISON ====================
    detailed_filename = f"detailed_comparison_{timestamp}.txt"
    with open(detailed_filename, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("TSCFLP ALGORITHM COMPARISON REPORT\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Timestamp: {results['timestamp']}\n\n")
        
        f.write("Instance Information:\n")
        f.write(f"  - Number of Primary Facilities: {results['instance_info']['num_primary']}\n")
        f.write(f"  - Number of Secondary Facilities: {results['instance_info']['num_secondary']}\n")
        f.write(f"  - Number of Customers: {results['instance_info']['num_customers']}\n")
        f.write(f"  - Total Demand: {results['instance_info']['total_demand']}\n\n")
        
        f.write("-"*70 + "\n")
        f.write("GREEDY ALGORITHM (Algorithm 1)\n")
        f.write("-"*70 + "\n")
        f.write(f"Cost: {greedy['cost']}\n")
        f.write(f"Execution Time: {greedy['execution_time_seconds']} seconds\n")
        f.write(f"Open Primary Facilities: {greedy['open_primary_facilities']}\n")
        f.write(f"Open Secondary Facilities: {greedy['open_secondary_facilities']}\n")
        f.write(f"Total Facilities Opened: {greedy['total_facilities_opened']}\n\n")
        
        f.write("-"*70 + "\n")
        f.write("MFSS ALGORITHM (Algorithm 2)\n")
        f.write("-"*70 + "\n")
        f.write(f"Cost: {mfss['cost']}\n")
        f.write(f"Execution Time: {mfss['execution_time_seconds']} seconds\n")
        f.write(f"Open Primary Facilities: {mfss['open_primary_facilities']}\n")
        f.write(f"Open Secondary Facilities: {mfss['open_secondary_facilities']}\n")
        f.write(f"Total Facilities Opened: {mfss['total_facilities_opened']}\n\n")
        
        f.write("="*70 + "\n")
        f.write("COMPARISON SUMMARY\n")
        f.write("="*70 + "\n")
        f.write(f"Cost Difference: {comp['cost_difference']} ")
        f.write(f"({'MFSS better' if comp['cost_difference'] > 0 else 'Greedy better'})\n")
        f.write(f"Cost Improvement: {comp['cost_improvement_percentage']}%\n")
        f.write(f"Better Algorithm: {comp['better_algorithm']}\n")
        f.write(f"Time Difference: {comp['time_difference_seconds']} seconds ")
        f.write(f"({'Greedy faster' if comp['greedy_faster'] else 'MFSS faster'})\n\n")
        
        f.write("="*70 + "\n")
        
    print(f"✓ Detailed report saved to: {detailed_filename}")


def print_summary(results):
    """In ra màn hình tóm tắt kết quả"""
    
    print("\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)
    
    greedy = results["algorithms"]["Greedy"]
    mfss = results["algorithms"]["MFSS"]
    comp = results["comparison"]
    
    print(f"\n{'Metric':<30} {'Greedy':<20} {'MFSS':<20}")
    print("-"*70)
    print(f"{'Cost':<30} {greedy['cost']:<20} {mfss['cost']:<20}")
    print(f"{'Execution Time (s)':<30} {greedy['execution_time_seconds']:<20} {mfss['execution_time_seconds']:<20}")
    print(f"{'Open Primary Facilities':<30} {greedy['num_open_primary']:<20} {mfss['num_open_primary']:<20}")
    print(f"{'Open Secondary Facilities':<30} {greedy['num_open_secondary']:<20} {mfss['num_open_secondary']:<20}")
    print("-"*70)
    print(f"\nCost Improvement: {comp['cost_improvement_percentage']}%")
    print(f"Better Algorithm: {comp['better_algorithm']}")
    print(f"Greedy is {'faster' if comp['greedy_faster'] else 'slower'} than MFSS")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("Starting algorithm comparison...\n")
    
    # Run comparison
    results = run_comparison()
    
    # Save results to files
    save_results(results)
    
    # Print summary
    print_summary(results)
    
    print("\n✓ Comparison completed successfully!")

