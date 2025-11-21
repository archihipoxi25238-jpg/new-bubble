# Bubble 可视化应用

一个简单的可视化工具，用于创建「bubble」来记录你的想法，并为每个想法快速获取网络上的相关资讯。

## 功能
- 为每个新想法创建独立的 bubble，持续累积。
- 查看所有 bubble，包含想法描述与已经收集的资料。
- 通过 DuckDuckGo Instant Answer API 获取在线资料；在离线环境中会返回友好提示。
- 提供 Web 界面管理 bubble，并可实时刷新内容。
- 页面顶部会显示后端连接状态，如遇 404/无法连接可据此快速排查。

## 安装与运行
1. 创建虚拟环境并安装依赖：
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. 启动 Web 应用：
   ```bash
   python app.py
   ```
   默认监听 `http://localhost:5000`。

   若看到页面提示「无法连接后端」，请确认上述命令仍在运行，并访问 `http://localhost:5000/api/health` 验证服务可用。

## 使用说明
1. 打开浏览器访问 `http://localhost:5000`。
2. 左侧面板填写「标题」和「想法描述」，点击「创建 Bubble」。
3. 每个 bubble 卡片中可输入关键词，点击「获取网上资讯」将相关内容追加到该 bubble 下方。
4. 点击「刷新」按钮重新拉取最新 bubble 数据。

所有数据会保存在当前目录下的 `bubbles.json` 文件中，方便再次打开继续使用。如需命令行版本，可运行 `python bubble.py`。
