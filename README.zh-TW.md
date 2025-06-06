# QuantConnect 交易機器人開發

[![授權條款: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](./README.md) | 繁體中文

本儲存庫致力於使用 QuantConnect 平台進行各種交易策略的開發與回測。

---

## 📖 關於本專案

這個專案是使用 QuantConnect 平台開發的交易策略集合。其中包含了一些基礎策略以及正在開發中的實驗性策略。

## 📂 專案結構

此儲存庫的結構如下：

-   `Quantconnect_Trading_Bot_Stratgies_Basic/`: 包含經過充分測試的基礎交易策略。這些策略通常比較穩定，適合作為學習範例。
-   `QuantConnect_Trading_Bot_Strategies_Dev/`: 包含正在開發中的實驗性策略。這些策略可能尚未完成或不穩定。

## 🚀 開始使用

您需要一個 QuantConnect 帳戶才能開始使用這些策略。您可以複製此儲存庫，並將策略檔案上傳到您的 QuantConnect 專案中。

### 先決條件

-   一個 [QuantConnect](https://www.quantconnect.com/) 帳戶。
-   具備 Python 和演算法交易的基礎知識。

### 安裝

1.  複製此儲存庫
    ```sh
    git clone https://github.com/your_username/QuantConnect_Trading_Bot_Dev_Public.git
    ```
2.  登入您的 QuantConnect 帳戶並建立一個新專案。
3.  將所需的策略檔案（例如，從 `Quantconnect_Trading_Bot_Stratgies_Basic/` 目錄中）上傳到您的 QuantConnect 專案。
4.  在 QuantConnect 平台上運行回測。

## 🐳 使用 Docker 進行本地回測

本專案已整合 Docker，讓您可以使用 LEAN 引擎輕鬆進行本地回測。

### 先決條件

-   已安裝 [Docker](https://www.docker.com/get-started) 和 [Docker Compose](https://docs.docker.com/compose/install/)。
-   您的 QuantConnect User ID 和 API Token。您可以在您的[帳戶頁面](https://www.quantconnect.com/account/)找到它們。

### 設定

1.  **設定您的憑證：**
    您需要提供您的 QuantConnect 憑證給 LEAN 引擎。在專案根目錄下建立一個名為 `.env` 的檔案。
    ```
    QC_USER_ID=YOUR_USER_ID
    QC_API_TOKEN=YOUR_API_TOKEN
    ```
    將 `YOUR_USER_ID` 和 `YOUR_API_TOKEN` 替換為您自己的憑證。此檔案已被 Git 忽略，所以您的憑證將會保持私密。

### 運行回測

1.  **開啟終端機**並移動到專案根目錄。
2.  使用 `docker-compose` **運行回測**。您需要指定您想運行的策略檔案路徑。

    例如，要運行 `BasicTemplateAlgorithm`：
    ```sh
    docker-compose run --rm lean backtest "Quantconnect_Trading_Bot_Stratgies_Basic/BasicTemplateAlgorithm.py"
    ```
3.  LEAN 引擎將會啟動，下載必要的數據，並運行回測。結果將會儲存在 `/backtests` 目錄中。

## 🤝 如何貢獻

貢獻是讓開源社群成為一個學習、啟發和創造的絕佳場所的原因。我們非常感謝您的任何貢獻。

若您希望做出貢獻，請 fork 此專案並建立一個 pull request。您也可以開啟一個 issue，並附上 "enhancement" 標籤。

1.  Fork 專案
2.  建立您的功能分支 (`git checkout -b feature/AmazingFeature`)
3.  提交您的變更 (`git commit -m 'Add some AmazingFeature'`)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  開啟 Pull Request

## 📜 授權條款

本專案採用 MIT 授權條款。詳情請見 `LICENSE` 檔案。 