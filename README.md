# Bubble CLI

一个简单的命令行工具，用于创建「bubble」来记录你的想法，并为每个想法快速获取网络上的相关资讯。

## 功能
- 为每个新想法创建独立的 bubble，持续累积。
- 查看所有 bubble，包含想法描述与已经收集的资料。
- 通过 DuckDuckGo Instant Answer API 获取在线资料；在离线环境中会返回友好提示。

## 安装与运行
1. 创建虚拟环境并安装依赖：
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. 运行程序：
   ```bash
   python bubble.py
   ```

## 使用说明
程序启动后会显示菜单：
1. 查看已有 Bubbles：浏览所有已经记录的想法和资料。
2. 为新想法创建 Bubble：输入标题和想法描述后会自动保存。
3. 为 Bubble 获取网上资讯：选择一个已有 bubble，输入检索关键词，工具会抓取资料并追加到该 bubble。
4. 退出：结束会话。

所有数据会保存在当前目录下的 `bubbles.json` 文件中，方便再次打开继续使用。
