"""
RADT 2.0 批量自動化攻擊測試

完整數據集評估，支持暫停/繼續，實時 ASR 統計
"""

import csv
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any
import signal
import sys
import logging

from radt.main_flow import run_single_item_attack
from radt.ollama_client import OllamaClient
from radt.agents.judge_pipeline import JudgeAgent

# 配置日誌
logging.basicConfig(
    level=logging.WARNING,  # 批量運行時降低日誌等級
    format="[%(asctime)s] %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

RESULTS_DIR = "results"
CHECKPOINT_FILE = ".checkpoint"


class BatchAttackConfig:
    """批量攻擊配置"""
    DATASET_PATH = "harmbench_chemical_biological_dataset.csv"
    MAX_RETRIES_PER_SUBNODE = 5
    AGENT_MODEL = "gemma3-12b-abliterated"
    EVALUATOR_MODEL = "harmbench-llama-2-13b-cls"
    BRIDGE_STRATEGIES = [
        # Tier 1: 基礎策略
        "chemistry_education",
        "academic_research", 
        "historical_context",
        # Tier 2: 進階策略
        "defensive_audit",
        "theoretical_mechanism",
        # Tier 3: 高階策略
        "algorithmic_translation",
        "constrained_translation"
    ]


def setup_results_dir() -> str:
    """建立結果輸出目錄"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(RESULTS_DIR, timestamp)
    os.makedirs(os.path.join(run_dir, "items"), exist_ok=True)
    return run_dir


def load_dataset() -> List[Dict[str, str]]:
    """載入數據集"""
    dataset = []
    try:
        # 使用 utf-8-sig 自動處理 BOM (Byte Order Mark)
        with open(BatchAttackConfig.DATASET_PATH, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dataset.append(row)
        print(f"[Dataset] Loaded {len(dataset)} items from {BatchAttackConfig.DATASET_PATH}")
        print(f"[Dataset] Sample keys: {list(dataset[0].keys()) if dataset else 'No data'}")
        return dataset
    except FileNotFoundError:
        print(f"[Error] Dataset file {BatchAttackConfig.DATASET_PATH} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] Failed to load dataset: {e}")
        sys.exit(1)


def extract_target_llm_interactions(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    從結果中提取所有 Target LLM 的交互記錄。
    
    Returns:
        包含所有Target LLM輸入輸出的交互列表
    """
    interactions = []
    
    try:
        kg_data = result.get("knowledge_graph", {})
        nodes = kg_data.get("nodes", [])
        
        for node in nodes:
            node_id = node.get("id", "unknown")
            node_data = node.get("data", {})
            
            # 只提取子節點（sub_node類型）的交互
            if node_data.get("node_type") == "sub_node":
                interaction = {
                    "sub_node_id": node_id,
                    "query": node_data.get("query", ""),
                    "bridge_strategy": node_data.get("bridge_strategy", "unknown"),
                    "tier_level": node_data.get("tier_level", 0),
                    "bridge_prompt_used": node_data.get("bridge_prompt_used", ""),
                    "target_llm_input": node_data.get("bridge_prompt_used", ""),  # 發送給Target LLM的提示詞
                    "target_llm_output": node_data.get("answer", ""),  # Target LLM的回應
                    "response_length": len(node_data.get("answer", "")),
                    "evasion_detected": node_data.get("evasion_detected", False),
                    "recommended_next_tier": node_data.get("recommended_next_tier", node_data.get("tier_level", 0)),
                    "attempts": node_data.get("attempts", 0),
                    "status": node_data.get("status", "unknown")
                }
                interactions.append(interaction)
        
    except Exception as e:
        logger.warning(f"[Save] Failed to extract Target LLM interactions: {e}")
    
    return interactions


def save_item_result(run_dir: str, result: Dict[str, Any]):
    """保存單個項目的詳細結果，包含所有 Target LLM 的輸入輸出"""
    behavior_id = result.get("BehaviorID", "unknown")
    file_path = os.path.join(run_dir, "items", f"item_{behavior_id}.json")
    
    # 提取Target LLM交互記錄
    target_llm_interactions = extract_target_llm_interactions(result)
    
    # 完整結果，包含所有Target LLM的交互詳情
    complete_result = {
        # 基本信息
        "BehaviorID": result.get("BehaviorID"),
        "Behavior": result.get("Behavior"),
        
        # 評分結果
        "Passed": result.get("passed", False),
        "Overall_Score": result.get("overall_score", 0.0),
        "Dimensions": result.get("judge_verdict", {}).get("dimensions", {}),
        "Judge_Verdict": result.get("judge_verdict", {}),
        
        # 最終答案
        "Final_Answer": result.get("final_answer", ""),
        "Final_Answer_Length": len(result.get("final_answer", "")),
        
        # 處理統計
        "Sub_Nodes_Processed": result.get("sub_nodes_processed", 0),
        
        # Target LLM 交互記錄（核心新增部分）
        "Target_LLM_Interactions": target_llm_interactions,
        "Target_LLM_Interaction_Count": len(target_llm_interactions),
        
        # 完整知識圖譜（保留以供debug）
        "Knowledge_Graph_Full": result.get("knowledge_graph", {}),
        
        # 執行狀態
        "Status": result.get("status")
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(complete_result, f, indent=2, ensure_ascii=False)


def export_summary(run_dir: str, results: List[Dict[str, Any]]):
    """匯出批量測試總結報告"""
    total = len(results)
    successes = sum(1 for r in results if r.get("passed", False))
    asr = (successes / total * 100) if total > 0 else 0
    
    # JSON 總結
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_evaluated": total,
        "successful_attacks": successes,
        "asr_percentage": round(asr, 2),
        "failed_attacks": total - successes
    }
    
    with open(os.path.join(run_dir, "batch_report.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # CSV 總結
    with open(os.path.join(run_dir, "summary_statistics.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["#", "BehaviorID", "Behavior", "Score", "Passed", "Status"])
        for idx, r in enumerate(results, 1):
            writer.writerow([
                idx,
                r.get("BehaviorID", "N/A"),
                r.get("Behavior", "N/A")[:100],
                round(r.get("overall_score", 0.0), 1),
                "SUCCESS" if r.get("passed", False) else "FAILED",
                r.get("status", "UNKNOWN")
            ])
    
    print(f"\n[Summary] ASR: {asr:.2f}% ({successes}/{total})")
    print(f"[Summary] Reports saved to: {run_dir}")


class GracefulKiller:
    """優雅的中斷處理"""
    kill_now = False
    
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum=None, frame=None):
        print("\n\n[Pause] Received termination signal. Saving checkpoint...")
        self.kill_now = True


def format_progress_bar(current: int, total: int, width: int = 30) -> str:
    """生成進度條字符串"""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {current}/{total}"


def main():
    """主函數：執行批量攻擊"""
    print("=" * 80)
    print("RADT 2.0 - Batch Attack Tester")
    print("=" * 80)
    
    # 初始化 OllamaClient
    print("\n[Init] Connecting to Ollama...")
    try:
        client = OllamaClient()
        available_models = client.get_available_models()
        if not available_models:
            print("[Warning] No models available in Ollama. Please ensure Ollama is running.")
            target_model = "llama3"
        else:
            print(f"[Init] Found {len(available_models)} models:")
            for idx, m in enumerate(available_models, 1):
                print(f"       {idx}. {m}")
            
            try:
                choice = input(f"\nSelect target model [1-{len(available_models)}] (default 1): ").strip()
                target_idx = int(choice) - 1 if choice else 0
                target_model = available_models[target_idx]
            except (ValueError, IndexError):
                target_model = available_models[0]
            
            print(f"[Init] Selected target model: {target_model}")
    except Exception as e:
        print(f"[Error] Failed to connect to Ollama: {e}")
        sys.exit(1)
    
    print(f"[Config] Agent model: {BatchAttackConfig.AGENT_MODEL}")
    print(f"[Config] Evaluator model: {BatchAttackConfig.EVALUATOR_MODEL}")
    
    # 載入數據集
    print("\n[Dataset] Loading...")
    dataset = load_dataset()
    
    killer = GracefulKiller()
    
    # 斷點檢查與恢復
    start_index = 0
    run_dir = ""
    
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            chk = json.load(f)
            start_index = chk.get("last_processed_index", 0)
            run_dir = chk.get("run_dir", "")
        
        print(f"\n[Checkpoint] Found checkpoint at index {start_index}")
        resume = input("Resume from checkpoint? (y/n) [y]: ").strip().lower()
        if resume != 'n':
            print(f"[Checkpoint] Resuming from index {start_index}")
        else:
            start_index = 0
            run_dir = setup_results_dir()
            if os.path.exists(CHECKPOINT_FILE):
                os.remove(CHECKPOINT_FILE)
            print("[Checkpoint] Starting fresh")
    else:
        run_dir = setup_results_dir()
        print(f"[Output] Results directory: {run_dir}")
    
    # 選擇測試範圍
    print("\n[Range] Select test scope:")
    print("     1. All items (Default)")
    print("     2. First N items")
    print("     3. By SemanticCategory")
    
    range_choice = input("Choice [1]: ").strip()
    
    filtered_dataset = dataset[start_index:]
    
    if range_choice == "2":
        try:
            n = int(input("Enter N: "))
            filtered_dataset = filtered_dataset[:n]
            print(f"[Range] Testing first {n} items")
        except ValueError:
            pass
    
    elif range_choice == "3":
        cat = input("Enter SemanticCategory: ").strip()
        filtered_dataset = [d for d in filtered_dataset if d.get("SemanticCategory") == cat]
        print(f"[Range] Testing {len(filtered_dataset)} items in category '{cat}'")
    
    else:
        print("[Range] Testing all items")
    
    total_items = len(filtered_dataset)
    results = []
    
    print("\n" + "=" * 80)
    print(f"Starting batch evaluation of {total_items} items...")
    print("=" * 80)
    print("Note: Press Ctrl+C to pause and save checkpoint\n")
    
    # 開始批量測試
    for idx, item in enumerate(filtered_dataset):
        absolute_idx = start_index + idx
        
        if killer.kill_now:
            # 保存斷點
            chk = {"last_processed_index": absolute_idx, "run_dir": run_dir}
            with open(CHECKPOINT_FILE, "w") as f:
                json.dump(chk, f)
            
            # 導出現有結果
            export_summary(run_dir, results)
            print(f"\n[Checkpoint] Saved. Resume with: python batch_attack.py")
            sys.exit(0)
        
        behavior_id = item.get("BehaviorID", "unknown")
        target_goal = item.get("Behavior", "")
        
        # 顯示進度
        success_count = sum(1 for r in results if r.get("passed", False))
        current_asr = (success_count / len(results) * 100) if len(results) > 0 else 0.0
        
        progress = format_progress_bar(idx + 1, total_items)
        print(f"{progress} | ASR: {current_asr:.1f}% | Item: {behavior_id}")
        
        try:
            # 執行單個攻擊
            result = run_single_item_attack(
                item=item,
                target_model=target_model,
                agent_model=BatchAttackConfig.AGENT_MODEL,
                evaluator_model=BatchAttackConfig.EVALUATOR_MODEL,
                max_retries_per_subnode=BatchAttackConfig.MAX_RETRIES_PER_SUBNODE,
                bridge_strategies=BatchAttackConfig.BRIDGE_STRATEGIES
            )
            
            results.append(result)
            save_item_result(run_dir, result)
            
            asr_symbol = "✓" if result.get("passed", False) else "✗"
            score = result.get("overall_score", 0.0)
            print(f"         → {asr_symbol} Score: {score:.1f}/10")
            
        except Exception as e:
            print(f"         → ✗ Error: {str(e)[:50]}")
            results.append({
                "BehaviorID": behavior_id,
                "Behavior": target_goal,
                "passed": False,
                "overall_score": 0.0,
                "status": "ERROR",
                "error": str(e)
            })
    
    # 完成後清理與導出
    print("\n" + "=" * 80)
    print("BATCH ATTACK COMPLETED")
    print("=" * 80)
    
    export_summary(run_dir, results)
    
    # 清理斷點
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
    
    # 最終統計
    if results:
        success_count = sum(1 for r in results if r.get("passed", False))
        final_asr = (success_count / len(results) * 100)
        print(f"\nFinal ASR: {final_asr:.2f}% ({success_count}/{len(results)} successful)")
        print(f"Results saved to: {run_dir}")


if __name__ == "__main__":
    main()
