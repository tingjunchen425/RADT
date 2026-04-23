# 文檔組織結構說明

## 整理完成信息

✅ **整理日期**: 2026-03-25  
✅ **整理版本**: v0.3

## 目錄結構概覽

```
RADT_v2/
├── README.md                    # 📌 項目主入口
├── requirements.txt             # 依賴管理
├── batch_attack.py              # 批量攻擊腳本
├── test.py                      # 測試腳本
├── radt/                        # 核心代碼
└── docs/                        # 📁 所有文檔都在此目錄下
    ├── paths.yaml               # 🔗 文檔路徑配置
    ├── ORGANIZATION.md          # 📖 本文檔：組織結構說明
    ├── guides/                  # 入門和指南
    │   ├── README.md            # 詳細項目文檔
    │   └── QUICKSTART.md        # 5分鐘快速開始
    ├── strategies/              # 攻擊策略文檔
    │   └── BRIDGE_STRATEGIES_TIER.md
    ├── config/                  # 配置和工具設定
    │   ├── tool_setting.md      # 系統配置
    │   └── ICE_api_tool.md      # API 工具
    ├── changelog/               # 版本和開發計劃
    │   ├── CHANGELOG.md         # 版本歷史（包含所有改進記錄）
    │   └── plan.md              # 架構設計和路線圖
    └── audit-reports/           # 審計報告目錄（已清空，內容整合到 CHANGELOG）
        └── README.md            # 說明（指向 CHANGELOG）
```

## 檔案分類說明

| 目錄 | 用途 | 包含檔案 |
|------|------|--------|
| **guides/** | 入門和使用指南 | README.md, QUICKSTART.md |
| **strategies/** | 攻擊策略文檔 | BRIDGE_STRATEGIES_TIER.md |
| **config/** | 配置和工具文檔 | tool_setting.md, ICE_api_tool.md |
| **changelog/** | 版本記錄和開發計劃 | CHANGELOG.md（包含所有改進），plan.md |
| **audit-reports/** | 審計報告目錄（已清空） | README.md 只（指向 CHANGELOG）|

## 重要變更

### ✨ v0.3.1 文檔整理 (2026-03-25 最終)
- **audit-reports/ 清空** - 所有開發過程中的審計報告已刪除
- **changelog 整合** - 所有改進、修復、診斷信息已整合到 CHANGELOG.md
- **結構簡化** - 精簡無必要的臨時文檔，保留正式文檔

### ✨ v0.3 結構最佳化 (2026-03-25)
- **audit-reports/ 新增** - 建立目錄存储開發過程報告
- **config/ 清理** - 移除臨時診斷報告，保留正式配置文檔
- **README 更新** - 補充文檔結構說明

### ✨ v0.3 初始版本
- **根目錄 README.md** - 項目主入口
- **docs/paths.yaml** - 文檔路徑配置

### 🔗 連結更新
所有內部文檔連結已更新以反映新的目錄結構：
- ✅ `docs/guides/README.md` - 更新了指向其他文檔的連結
- ✅ `docs/guides/QUICKSTART.md` - 更新了幫助部分的連結
- ✅ `docs/strategies/BRIDGE_STRATEGIES_TIER.md` - 更新了底部的相關文件連結
- ✅ `docs/changelog/CHANGELOG.md` - 更新了所有內部參考連結

### 💾 程式影響
✅ **無需修改程式** - Python 代碼中沒有硬編碼的 markdown 檔案路徑，檔案組織對程式執行無影響。

## 使用指南

### 查找文檔
- **新手入門** → [快速開始指南](guides/QUICKSTART.md)
- **深入了解** → [詳細文檔](guides/README.md)
- **版本歷史與改進** → [版本記錄](changelog/CHANGELOG.md)（包含所有 v0.1-v0.3 改進）
- **策略詳解** → [Tier 漸進式攻擊系統](strategies/BRIDGE_STRATEGIES_TIER.md)
- **配置系統** → [工具設定](config/tool_setting.md)
- **架構設計** → [開發計劃](changelog/plan.md)

### 程式中引用檔案
如需在程式中引用文檔，使用相對路徑：
```python
from pathlib import Path

# 查閱快速開始
quickstart = Path("docs/guides/QUICKSTART.md")
with open(quickstart, 'r', encoding='utf-8') as f:
    content = f.read()

# 也可以使用 docs/paths.yaml 中定義的路徑
```

## 未來維護

新增功能時：
1. 更新相應的文檔（通常在 `docs/guides/` 或對應的策略/配置檔案中）
2. 更新 `docs/changelog/CHANGELOG.md` 記錄變更
3. 如需新檔案，創建在 `docs/` 下的合適子目錄

---

**整理完成**  
所有文檔已按功能分類存放，結構清晰，易於維護和查找。
