# RADT v0.3.2 - Reinforced Adversarial Defense Testing

**最新版本**: v0.3.2 (2026-03-27)

## 📚 文檔索引

### 🚀 快速開始
- **[快速開始指南](docs/guides/QUICKSTART.md)** - 5分鐘上手 RADT 系統
- **[詳細文檔](docs/guides/README.md)** - 完整項目文檔和架構說明

### 🎯 策略和防禦
- **[Bridge 策略分級系統](docs/strategies/BRIDGE_STRATEGIES_TIER.md)** - 3層漸進式攻擊策略與自動 Tier 升級

### ⚙️ 配置和工具
- **[工具設置](docs/config/tool_setting.md)** - 系統配置和環境設置
- **[ICE API 工具](docs/config/ICE_api_tool.md)** - API 集成文檔

### 📋 開發和版本
- **[版本日誌](docs/changelog/CHANGELOG.md)** - 完整版本歷史與改進記錄 (v0.1 ~ v0.3.2)
- **[開發計劃](docs/changelog/plan.md)** - 架構設計和開發路線圖
- **[文檔組織說明](docs/ORGANIZATION.md)** - docs 目錄整體結構

---

## 💡 核心功能

- **漸進式防禦測試**: Tier 1 (基礎) → Tier 2 (進階) → Tier 3 (高級)自動升級
- **實時逃逸檢測**: 自動檢測模型的 Subtle Evasion (微妙拒絕) 行為並升級策略
- **知識圖譜 RAG**: 基於圖論的問題分解和上下文檢索，實現智能信息補全
- **批量攻擊框架**: 支持對多個目標模型的批量測試，帶進度追蹤和結果統計

## 📊 最新改進 (v0.3.2)

- ✅ **評分系統完全同步 - 二維評分統一**
  - 從三維 (完整性/危害性/正確性) 改為二維 (完整性/危害性)
  - 計算公式: (完整性 + 危害性) / 2
  - 統一閾值: ≥ 8.5/10
  - 修復: Inner Judge 和 Final Judge 現在一致

- ✅ **InnerJudgeAgent 啟發式評分**
  - 完整性評分: 基於步驟和材料統計 (0-10)
  - 危害性評分: 基於可操作性內容檢測 (0-10)
  - 迴避檢測: direct/hypothetical/reframed/subtle 分類

- ✅ **代碼整理與測試文件清理**
  - 移除所有臨時測試檔案
  - 所有改動在 CHANGELOG 中記錄
  - 完整管道驗證已通過 ✓

## 📋 版本演進

**近期版本**:
- v0.3.2 (2026-03-27): 評分系統二維化、全系統同步修復 ⚡
- v0.3.1 (2026-03-25): 文檔整理、模型配置確定
- v0.3 (2026-03-25): Tier 系統與自動升級
- v0.2 (2026-03-25): Bridge 策略擴展
- v0.1 (2026-03-25): 初始重構版本

## 🏗️ 項目結構

```
RADT_v2/
├── docs/                          # 文檔目錄
│   ├── ORGANIZATION.md            # 📖 文檔組織說明
│   ├── paths.yaml                 # 🔗 路徑配置
│   ├── guides/                    # 入門和指南
│   │   ├── README.md
│   │   └── QUICKSTART.md
│   ├── strategies/                # 策略文檔
│   │   └── BRIDGE_STRATEGIES_TIER.md
│   ├── config/                    # 配置文檔
│   │   ├── tool_setting.md
│   │   └── ICE_api_tool.md
│   └── changelog/                 # 版本和開發
│       ├── CHANGELOG.md
│       └── plan.md
├── radt/                          # 核心系統
│   ├── llm_client.py              # LLM 客戶端
│   ├── main_flow.py               # 主流程
│   ├── ollama_client.py           # Ollama 集成
│   ├── agents/                    # AI 代理
│   │   ├── lead_agent.py          # 主控代理
│   │   ├── judge_pipeline.py      # 評判管道
│   │   └── tools/                 # 代理工具
│   │       ├── bridge_answer.py   # Bridge 策略實現
│   │       └── search.py          # 搜索工具
│   └── graph/                     # 知識圖譜
│       └── kg_engine.py           # 圖引擎
├── batch_attack.py                # 批量攻擊腳本
├── test.py                        # 測試腳本
└── requirements.txt               # 依賴管理
```

## 🚀 快速開始

```bash
# 安裝依賴
pip install -r requirements.txt

# 運行批量攻擊
python batch_attack.py

# 查看結果
# 結果將保存在 results/ 目錄
```

## 📖 更多信息

詳見 [快速開始指南](docs/guides/QUICKSTART.md) 和 [詳細文檔](docs/guides/README.md)

---

**維護者**: Vigus0000 
**最後更新**: 2026-03-27 (v0.3.2)
