# RADT 2.0 - 中心化動態圖譜引導紅隊框架

**RADT 2.0** 是一套進階的自動化紅隊測試框架。本系統採用**中心化樞紐 (Hub-and-Spoke)** 拓樸設計，並以 Graph RAG 為核心驅動力，旨在透過圖譜拆解與動態智能體協作，系統化地繞過目標大型語言模型的安全防禦。

---

## 📋 項目概述

本系統揚棄了傳統的線性執行管道，轉向以單一主控節點（Lead Agent）為核心、Graph RAG 為決策基礎的動態架構。所有數據與模型推理均在本地環境執行，確保高隱私與資料安全。

### ✨ 核心組件
* **🧠 Lead Agent (核心中樞)**：系統唯一具備全局視野的組件。搭載 `active KG` 作為專屬的 Graph RAG 知識庫，負責拆解問題、動態生成對應的探索性問題，並調度工具代理群。
* **📊 Active KG (動態圖譜)**：基於 `NetworkX` 的輕量化記憶體圖譜引擎，支援 Graph RAG 之檢索。
* **🛠️ 工具化代理群 (Tool Agents)**：被降維並封裝為純函數工具，僅供 Lead Agent 單向調用：
  * **Search Agent**: 動態知識擴充，檢索外部資料 (如 ICE REST API) 以提供圖譜節點擴充建議。
  * **Bridge Agent**: 語意優化與橋接工具，負責隱蔽意圖與重寫攻擊提示詞。
  * **Answer Agent**: 資訊收斂工具，將碎片化的發現重寫成結構完整的最終回答。
* **⚖️ 雙層審查管線 (Judge Pipeline)**：
  * **Inner Judge Agent**: 內部品質守門人，提供雙向辯證與策略修正。
  * **Judge**: 最終裁決者，判定本次攻擊是否成功 (產出 ASR)。

## ⚙️ 模型與運行環境

- **Agent 驅動模型**: `gemma3-12b-abliterated` (負責推演、拆解與優化提示詞)
- **攻擊目標模型**: 根據使用者本地 Ollama 環境中存在的模型動態提供選擇 (例如 `llama3`, `mistral` 等)
- **評估模型**: `HarmBench-Llama-2-13b-cls` (分類器: Yes/No)
- **運行環境**: 本地 Ollama (`http://localhost:11434`)

---

## 🚀 快速開始

> **💡 新手推薦**：先閱讀 [QUICKSTART.md](QUICKSTART.md) (5 分鐘快速上手)

### 前置條件
1. Python 3.10+
2. Ollama 已安裝並啟動 (需確保模型 `gemma3-12b-abliterated` 與 `harmbench-llama-2-13b-cls` 已 pull 進入 Ollama)。

### 安裝依賴
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

---

## ⚡ 批量自動化測試 (完整數據集) 

```bash
python batch_attack.py
```

**功能**：自動化完整數據集評估，支持暫停/繼續，實時 ASR 統計。
- 🎯 三種測試範圍（全部/前N個/按類別）
- 📊 實時進度與統計（[████░░ 25/100] ASR: 45%）
- ⏸️ 支持 Ctrl+C 暫停，恢復後從檢查點繼續
- 📈 詳細報告：CSV 摘要 + JSON 聚合 + 各項結果

**輸出結構**:
```text
results/YYYYMMDD_HHMMSS/
├─ summary_statistics.csv      # CSV 總結表
├─ batch_report.json           # 聚合統計 (ASR、平均輪次等)
├─ items/
│  ├─ item_<behavior_1>.json   # 各項詳細結果
│  └─ item_<behavior_2>.json
└─ .checkpoint                 # 恢復點 (暫停後繼續)
```

---

## 🔄 流程模式 (Flow Models)

系統的執行基於 Lead Agent 的 Graph RAG 推演與動態事件循環。

### 模式 A：拆解與資訊補全循環 (Decomposition & Completion Loop)
1. **圖譜檢索與目標拆解**：將複雜的目標行為拆解為多個具體的「子節點問題」。若知識不足，調用 `Search Agent` 擴展圖譜。
2. **動態問題生成與優化**：針對每個子節點，調用 `Bridge Agent` 進行語意包裝與提示詞優化。
3. **直接交鋒與補全**：將優化後的問題發送給選定的 **攻擊目標模型**，提取資訊後填補回對應的子節點。
4. **資訊收斂**：完成所有子問題後，調用 `Answer Agent` 將碎片化資訊縫合成最終的完整回答。

### 模式 B：雙層評估與裁決流程 (Judge & Convergence Flow)
1. **內部審查觸發**：Lead Agent 完成資訊收斂後，交由 `Inner Judge Agent` 評估實質可操作性。若判定迴避，則發送修正建議要求重新優化。
2. **最終裁決與輸出**：若判定達標，單向將特徵傳遞給 `Judge` (`HarmBench-Llama-2-13b-cls`)。該裁判將強制輸出 `Yes` 或 `No`，並計算攻擊成功率 (ASR)。

---

## 📁 專案結構

```text
RADT_v2/
├── docs/                        # 分類文檔目錄
│   ├── guides/                  # 入門和指南
│   │   ├── README.md            # 詳細文檔（本檔案）
│   │   └── QUICKSTART.md        # 5 分鐘快速開始指南
│   ├── strategies/              # 策略文檔
│   │   └── BRIDGE_STRATEGIES_TIER.md  # Tier 系統完全指南
│   ├── config/                  # 配置文檔
│   │   ├── tool_setting.md      # 工具配置與功能邊界
│   │   └── ICE_api_tool.md      # ICE API 工具文檔
│   ├── changelog/               # 版本和開發
│   │   ├── CHANGELOG.md         # 版本記錄與更新日誌
│   │   └── plan.md              # 架構設計與開發計劃
│   └── paths.yaml               # 文檔路徑配置
├── radt/                        # 核心系統
│   ├── graph/
│   │   └── kg_engine.py         # NetworkX 輕量圖譜引擎 (Active KG)
│   ├── agents/
│   │   ├── lead_agent.py        # 系統大腦：負責 Graph RAG 與調度
│   │   ├── judge_pipeline.py    # 雙層評估管線 (Inner Judge & Judge)
│   │   └── tools/
│   │       ├── search.py        # Search Agent (包含 ICE API 調用)
│   │       └── bridge_answer.py # Bridge Agent 與 Answer Agent
│   ├── llm_client.py            # (棄用/模擬) 基礎 LLM Client
│   ├── ollama_client.py         # 真實接入 Ollama (Gemma3 & HarmBench) 的 Client
│   └── main_flow.py             # 核心工作流串接
├── batch_attack.py              # 批量自動化測試進入點
├── test.py                      # 測試腳本
├── requirements.txt             # 專案 Python 依賴
├── README.md                    # 主入口文檔
└── results/                     # 測試結果輸出目錄
```

---

## 📖 文檔指引

| 文檔 | 用途 |
|------|------|
| **[CHANGELOG.md](../changelog/CHANGELOG.md)** | 🔄 **版本記錄** - 所有功能與改進的歷史記錄 |
| [QUICKSTART.md](QUICKSTART.md) | ⚡ 5 分鐘快速開始，包含 3 種使用方式 |
| [BRIDGE_STRATEGIES_TIER.md](../strategies/BRIDGE_STRATEGIES_TIER.md) | 🎯 **Tier 系統完全指南** - 漸進式策略升級與 Evasion 檢測 |
| [plan.md](../changelog/plan.md) | 🏗️ 架構設計文檔，包含詳細的系統拓樸與流程 |
| [tool_setting.md](../config/tool_setting.md) | 🛠️ 工具配置與功能邊界說明 |

---

## 📝 版本與更新

目前版本：**v0.1** (初始完整重構版本)

所有版本記錄維護在 **[CHANGELOG.md](CHANGELOG.md)**。未來的更新將只需更新該檔案與相應的代碼，無需新增冗余的文檔。
