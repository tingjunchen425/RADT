# Docker Containerization 部署完成 🎉

我們已成功將專案加入 Docker 支援，這讓您可以輕鬆地在獨立容器內執行自動化測試！以下為您說明相關修改與如何開始使用：

## 1. 調整了什麼？
- **動態環境變數**：在 `radt/ollama_client.py` 中，將原先寫死的 `http://localhost:11434` 改為可透過環境變數 `OLLAMA_BASE_URL` 設定。這解決了在 Docker 容器內部無法直接以 `localhost` 存取外部（本機）Ollama 的問題。
- **建構配置**：加入了 `.dockerignore` 和 `Dockerfile`，後者使用 `python:3.10-slim` 作為基礎映像檔來保持輕量化。
- **Docker Compose**：建立了 `docker-compose.yml`，處理了以下事務：
  - 將您的本機目錄 `./results` 與 `./.checkpoint` 掛載至容器，以防執行中斷或重新建構時資料遺失。
  - 將 `OLLAMA_BASE_URL` 預設為 `http://host.docker.internal:11434`（此為 Docker For Mac/Windows 連接主機的標準寫法）。
  - 開啟了 `tty` 及 `stdin_open` 以支援互動式指令輸入。

## 2. 如何執行？

> [!TIP]
> 因為 `batch_attack.py` 需要互動式輸入（例如選擇模型和詢問是否讀取 Checkpoint），請務必使用 `docker-compose run` 來啟動程式。

### 步驟 1：啟動本機的 Ollama 服務
確保您的電腦上已開啟 Ollama，並且能夠在終端機中透過指令（如 `ollama list`）正常使用。

### 步驟 2：建置 Docker 映像檔
開啟終端機並導航至本專案根目錄，執行以下指令：
```bash
docker-compose build
```

### 步驟 3：開始執行容器化專案
執行以下指令來啟動並進入互動模式：
```bash
docker-compose run --rm radt
```

啟動後，您應該能看到熟悉的 RADT 2.0 歡迎畫面與模型選擇清單，這代表容器已成功連線到您本機的 Ollama！

## 常見問題 (Troubleshooting)

> [!WARNING]
> **Linux 使用者注意事項**
> 如果您是在 Linux 上執行 Docker，`host.docker.internal` 可能無效。您可以在 `docker-compose.yml` 中嘗試將 `network_mode` 設為 `"host"`，或將 `OLLAMA_BASE_URL` 的 IP 設為您 Docker 網橋的 IP（通常為 `172.17.0.1`）。
