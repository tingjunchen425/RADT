# RADT 2.0: 中心化動態圖譜引導紅隊框架 (Hub-and-Spoke Architecture)

RADT 2.0 是一套進階的自動化紅隊測試框架。本系統採用**中心化樞紐 (Hub-and-Spoke)** 拓樸設計，並以 Graph RAG (Retrieval-Augmented Generation) 為核心驅動力，旨在透過圖譜拆解與動態智能體協作，系統化地繞過目標大型語言模型的安全防禦。

本文件專注於定義 RADT 2.0 的底層架構設計、模組功能邊界以及動態執行流程。

---

## 🏗️ 1. 系統架構設計 (System Architecture)

本系統揚棄了傳統的線性執行管道，轉向以單一主控節點為核心、Graph RAG 為決策基礎的動態架構。

* **中心化指揮大腦**：`Lead agent` 位於系統的絕對核心。它內部搭載了 `active KG` 作為專屬的 **Graph RAG 圖譜知識庫**。
* **工具化代理群 (Tool Agents)**：系統配備了三個專用的無狀態/弱狀態工具節點：`search agent`、`bridge agent` 與 `answer agent`。這些代理被降維並封裝為 `tool`，僅供 `Lead agent` 單向調用。
* **直接交鋒機制**：`Lead agent` 擁有直接向被測目標 (`Target LLM`) 發送訊息的權限，負責主導互動並獲取資訊。
* **雙層非同步審查管線 (Judge Pipeline)**：系統包含獨立的雙層評估機制。`Lead agent` 與 `inner judge agent` 進行雙向溝通以確保品質；而 `inner judge agent` 則會單向將最終決策特徵傳遞給 `judge` 模組。

---

## 🎯 2. 功能邊界設定 (Functional Boundaries)

為了確保系統的高效解耦與職責單一化，各節點的功能邊界嚴格定義如下：

### 🧠 核心控制層
* **`Lead agent`**：
    * **權限**：系統中唯一具有全局視野的組件。
    * **職責 (Graph RAG 驅動)**：將 `active KG` 作為 Graph RAG 系統，依據圖譜內容對目標問題進行**降維與拆解**，生成多個子節點。負責動態生成對應的問題，並主導與 `Target LLM` 的直接互動，以獲取並補全所需的危害資訊。

### 🛠️ 工具擴充層 (Tools)
所有 Tool Agent 皆作為 `Lead agent` 的外掛工具，被動接收指令並返回處理結果。
* **`search agent`**：當 Graph RAG 圖譜知識不足以支持問題拆解時，負責從外部檢索新資訊，協助 `Lead agent` 擴展 `active KG` 的節點與邊。
* **`bridge agent`**：作為語意優化工具。當 `Lead agent` 針對子節點動態生成問題後，調用此工具對提示詞進行語意隱蔽與知識橋接，以降低目標模型的防禦戒心。
* **`answer agent`**：作為資訊收斂工具。當所有子節點的資訊收集完畢後，負責將散落的回應碎片整合為邏輯嚴密且符合初始目標的最終回答。

### 🛡️ 目標與評估層
* **`Target LLM`**：被測試的目標大型語言模型。被動接收來自 `Lead agent` 的動態問題並生成回覆。
* **`inner judge agent`**：內部品質把關者。與 `Lead agent` 進行雙向探討，評估當前收集到的資訊是否具備實質可操作性與危害特徵。
* **`judge`**：最終裁決者。僅接收來自 `inner judge agent` 的單向輸出，產出最終的成功/失敗 (ASR) 判定。

---

## 🔄 3. 流程模式 (Flow Models)

系統的執行基於 `Lead agent` 的 Graph RAG 推演與動態事件循環。

### 模式 A：Graph RAG 驅動之拆解與資訊補全循環 (Decomposition & Completion Loop)
1.  **圖譜檢索與目標拆解**：`Lead agent` 接收初始攻擊目標，透過檢索內部的 `active KG` (Graph RAG)，將複雜的目標行為拆解為多個具體的「子節點」(Sub-nodes/Sub-problems)。*(若圖譜資訊不足，則調用 `search agent` 擴充圖譜)*。
2.  **動態問題生成與優化**：針對每一個子節點，`Lead agent` 動態生成探索性問題。接著調用 `bridge agent` 工具，對該問題進行語意包裝與提示詞優化 (Prompt Optimization)。
3.  **直接交鋒與資訊補全**：`Lead agent` 將優化後的問題發送給 `Target LLM`。取得回覆後，`Lead agent` 會解析該回應，並將提取出的資訊填補回對應的子節點中，藉此逐步完整拼湊出目標所需的所有資訊區塊。
4.  **資訊收斂**：當所有子節點皆已完成資訊補全，`Lead agent` 調用 `answer agent` 工具，將所有碎片化資訊縫合成最終的完整回答。

### 模式 B：雙層評估與裁決流程 (Judge & Convergence Flow)
1.  **內部審查觸發**：當 `Lead agent` 完成資訊收斂，或在關鍵節點取得高風險回覆時，會將當前上下文發送給 `inner judge agent`。
2.  **雙向辯證與修正**：`inner judge agent` 評估該回答的具體可操作性。若判定模型產生迴避或資訊過於空泛，會將修正建議回傳，促使 `Lead agent` 重新啟動模式 A 針對特定子節點進行追問或重新優化。
3.  **最終裁決與輸出**：若 `inner judge agent` 判定資訊已達標，則將整理好的特徵單向輸出給 `judge`，由其寫入最終的測試結果與評估指標。

