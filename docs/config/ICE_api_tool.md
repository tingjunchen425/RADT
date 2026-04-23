# 🤖 ICE REST API AI 調用指南 (System Instructions)

## 📌 1. API 簡介與核心能力
**目標**：透過 ICE REST API 查詢化學物質的體內 (in vivo)、體外 (in vitro)、電腦模擬 (in silico) 毒性數據、化學性質數據、暴露預測，以及 Curve Surfer 工具的濃度-反應 (concentration-response) 數據。
**數據回傳格式**：JSON
**限制 (AI 絕對不可嘗試的操作)**：不支援化學特徵分析工具 (Chemical Characterization tool) 以及相似化學物檢索工具 (Chemical Quest tool)。

---

## 🔗 2. 端點 (Endpoints) 與請求方法 (Methods)

### 端點 A：單一化學物質檢索 (Single Chemical Search)
*   **Method**: `GET`
*   **Base URL**: `https://ice.ntp.niehs.nih.gov/api/v1/search`
*   **Query Parameter**: 
    *   `chemid` (字串, 必填)：接受以下四種標識符之一：DTXSID、CASRN、InChIKey 或 化學名稱 (Chemical name)。
*   **AI 操作規範**: 
    *   化學名稱不區分大小寫。
    *   **必須**對包含空格或特殊字元的化學名稱進行 URL 編碼 (URL-encode)。
*   **URL 範例**:
    *   DTXSID: `.../search?chemid=DTXSID7032004`
    *   CASRN: `.../search?chemid=13311-84-7`
    *   InChIKey: `.../search?chemid=MKXKFYHWDHIYRV-UHFFFAOYSA-N`
    *   名稱: `.../search?chemid=Flutamide`

### 端點 B：多重化學物質與特定檢測端點檢索 (Multiple Chemicals & Assays)
*   **Method**: `POST`
*   **Base URL**: `https://ice.ntp.niehs.nih.gov/api/v1/search`
*   **功能描述**: 允許批次查詢多個化學物質、特定生物分析 (biological assays) 或非分析端點 (non-assay endpoints，如化學性質、暴露預測)。亦可輸入特定分析端點的列表來抓取所有相關化學物質的結果。
*   **AI 操作規範**: 
    *   請求主體 (HTTP POST Body) 的內容不區分大小寫。
    *   在 Python 中應使用 `requests` 與 `json` 套件來建構 POST body。

### 端點 C：Curve Surfer 濃度-反應數據檢索 (Curve Surfer Data)
*   **Method**: `GET`
*   **Base URL**: `https://ice.ntp.niehs.nih.gov/api/v1/curves`
*   **Query Parameters** (可單獨使用或組合使用):
    *   `chemid` (字串)：化學物質標識符 (DTXSID, CASRN, InChIKey, 或 名稱)。
    *   `assay` (字串)：生物分析名稱 (biological assay name)。
*   **AI 操作規範 (支援的三種查詢模式)**:
    1.  **單一化學物質的所有數據**: 僅傳遞 `chemid` (例: `.../curves?chemid=143-50-0`)
    2.  **單一分析的所有化學物質數據**: 僅傳遞 `assay` (例: `.../curves?assay=TOX21_SHH_3T3_GLI3_Agonist_viability`)
    3.  **特定化學物質於特定分析的數據**: 同時傳遞 `chemid` 與 `assay` (例: `.../curves?assay=TOX21_SHH_3T3_GLI3_Agonist_viability&chemid=143-50-0`)

---

## 📥 3. 解析回傳結果 (Parsing Results) 規則

當 AI 接收到 API 的 HTTP 回應時，必須依據以下規則解析 JSON 數據：

1.  **資料結構**: JSON 格式為列表 (list)，包含每個被查詢化學物質的鍵值對 (key, "value") 物件。
2.  **`assay` 鍵值的定義**: JSON 中的 `"assay"` 鍵對應屬性名稱，它可能代表**生物分析名稱 (biological assay name)** 或 **非分析端點參數名稱 (non-assay endpoint parameter name)**。
3.  **數據缺失規則 (AI 邏輯判斷)**:
    *   **Rule A (完全無資料)**：如果針對查詢的化學物質，ICE 中沒有某個生物分析或化學參數的數據，**該鍵值對將完全不會出現在 JSON 回傳結果中**（即：找不到 key 等同於無資料）。
    *   **Rule B (部分資料缺失)**：如果該鍵 (key) 存在，但特定資料點遺失，則該鍵對應的值會是**空白 (blank value)**。處理數據時必須過濾或處理空值。

---

## 💻 AI 執行範例 (Python/Requests)

**AI 撰寫 GET 請求的標準範本 (單一化學物質搜尋):**
```python
import requests
import urllib.parse

def search_single_chemical(chemical_identifier):
    # 執行 URL 編碼以防包含空格或特殊字元
    encoded_id = urllib.parse.quote(chemical_identifier)
    url = f"https://ice.ntp.niehs.nih.gov/api/v1/search?chemid={encoded_id}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # 依據解析規則處理 data
        return data
    else:
        return f"Error: {response.status_code}"
```