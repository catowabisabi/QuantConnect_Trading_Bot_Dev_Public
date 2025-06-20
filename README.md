# QuantConnect Trading Bot Development

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English | [繁體中文](./README.zh-TW.md)

This repository is dedicated to the development and backtesting of various trading strategies using the QuantConnect platform.

---

## 📖 About The Project

This project serves as a collection of trading strategies developed for the QuantConnect platform. It includes both foundational strategies and more experimental ones currently under development.

## 📂 Project Structure

The repository is organized into the following directories:

-   `Quantconnect_Trading_Bot_Stratgies_Basic/`: Contains well-tested, foundational trading strategies. These are generally more stable and serve as good examples for learning.
-   `QuantConnect_Trading_Bot_Strategies_Dev/`: Contains experimental strategies that are currently in development. These may be incomplete or unstable.

## 🚀 Getting Started

To get started with these strategies, you'll need a QuantConnect account. You can clone this repository and upload the strategy files to your QuantConnect projects.

### Prerequisites

-   A [QuantConnect](https://www.quantconnect.com/) account.
-   Basic knowledge of Python and algorithmic trading.

### Installation

1.  Clone the repo
    ```sh
    git clone https://github.com/your_username/QuantConnect_Trading_Bot_Dev_Public.git
    ```
2.  Navigate to your QuantConnect account and create a new project.
3.  Upload the desired strategy file (e.g., from the `Quantconnect_Trading_Bot_Stratgies_Basic/` directory) to your QuantConnect project.
4.  Run a backtest on the QuantConnect platform.

## 🐳 Local Backtesting with Docker

This project is equipped with Docker to allow for easy local backtesting using the LEAN engine.

### Prerequisites

-   [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed.
-   Your QuantConnect User ID and API Token. You can find them on your [account page](https://www.quantconnect.com/account/).

### Setup

1.  **Set up your credentials:**
    You need to provide your QuantConnect credentials to the LEAN engine. Create a file named `.env` in the root of the project.
    ```
    QC_USER_ID=YOUR_USER_ID
    QC_API_TOKEN=YOUR_API_TOKEN
    ```
    Replace `YOUR_USER_ID` and `YOUR_API_TOKEN` with your actual credentials. This file is ignored by Git, so your credentials will remain private.

### Running a Backtest

1.  **Open a terminal** and navigate to the project root directory.
2.  **Run the backtest** using `docker-compose`. You need to specify the path to the strategy file you want to run.

    For example, to run the `BasicTemplateAlgorithm`:
    ```sh
    docker-compose run --rm lean backtest "Quantconnect_Trading_Bot_Stratgies_Basic/BasicTemplateAlgorithm.py"
    ```
3.  The LEAN engine will start, download the necessary data, and run the backtest. The results will be stored in the `/backtests` directory.

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
