# Docker Containerization Plan

這個計畫將為專案新增 Docker 支援，讓您可以輕鬆地在任何環境下透過容器執行專案，同時能夠連接到本機的 Ollama 服務。

## User Review Required

> [!IMPORTANT]
> - 本專案的執行是互動式的（例如會透過終端機詢問要不要從 checkpoint 恢復、要選擇哪個模型等）。在 Docker 中執行互動式程式時，我們建議使用 `docker-compose run` 來執行，或者在 `docker run` 時加上 `-it` 參數。這部分已設計在後續的使用說明中。
> - 我們預設將 Docker 的 Ollama URL 指向 `http://host.docker.internal:11434`，這樣它就能直接存取到你本機（Host）上運行的 Ollama。如果您是使用 Linux 作業系統，可能需要額外的設定（如 `--add-host`）來支援此功能。

## Proposed Changes

---

### Docker Configuration
建立 Docker 相關的配置檔以容器化應用程式。

#### [NEW] .dockerignore
忽略不需要被打包進 Docker 映像檔的檔案和目錄，如 `.git`, `__pycache__`, `results` 等，以縮小映像檔體積並加快建置速度。

#### [NEW] Dockerfile
基於 `python:3.10-slim` 建立輕量級 Python 執行環境：
- 複製 `requirements.txt` 並安裝相依套件。
- 複製專案原始碼。
- 設定預設指令以支援執行 `batch_attack.py` 腳本。

#### [NEW] docker-compose.yml
定義一個名為 `radt` 的服務：
- 將本機的 `results` 與 `.checkpoint` 檔案掛載至容器內，確保執行結果與進度可以保存在您的本機。
- 設定環境變數 `OLLAMA_BASE_URL=http://host.docker.internal:11434` 以連接本機 Ollama 服務。
- 開啟 `stdin_open: true` 與 `tty: true` 以支援互動式的命令列輸入。

---

### Python Code Modifications
修改程式碼以支援環境變數的覆蓋，從而兼容 Docker 的內部網路架構。

#### [MODIFY] radt/ollama_client.py
原先 Ollama 的預設位址被硬編碼為 `http://localhost:11434`。在 Docker 容器內，`localhost` 會指向容器本身而不是您的主機。
- 我們將修改初始化邏輯，優先讀取 `OLLAMA_BASE_URL` 環境變數。如果未設定，則回退到預設的 `http://localhost:11434`。

---

## Verification Plan

### Automated Tests
目前專案沒有明確的單元測試框架，但我們可以透過建置映像檔來確認語法與環境無誤：
1. 執行 `docker-compose build` 確保 Dockerfile 與 `requirements.txt` 可正確安裝。

### Manual Verification
1. 使用指令 `docker-compose run --rm radt python batch_attack.py` 啟動系統。
2. 驗證是否能成功連線至本機的 Ollama 並列出可用模型。
3. 驗證互動式選單可以正常接收輸入。
4. 驗證執行結果（如 `.checkpoint` 與 `results/` 目錄內的文件）是否會正確生成於本機的對應資料夾。
