import json
import os
import textwrap
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests

DATA_FILE = "bubbles.json"


@dataclass
class Bubble:
    id: int
    title: str
    idea: str
    created_at: str
    resources: List[Dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bubble":
        return cls(
            id=data["id"],
            title=data["title"],
            idea=data["idea"],
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            resources=data.get("resources", []),
        )


class BubbleManager:
    def __init__(self, path: str = DATA_FILE) -> None:
        self.path = path
        self.bubbles: List[Bubble] = []
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.path):
            self.bubbles = []
            return

        with open(self.path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        self.bubbles = [Bubble.from_dict(item) for item in data]

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as fp:
            json.dump([asdict(b) for b in self.bubbles], fp, ensure_ascii=False, indent=2)

    def create_bubble(self, title: str, idea: str) -> Bubble:
        next_id = (max((b.id for b in self.bubbles), default=0) + 1)
        bubble = Bubble(
            id=next_id,
            title=title,
            idea=idea,
            created_at=datetime.utcnow().isoformat(),
        )
        self.bubbles.append(bubble)
        self.save()
        return bubble

    def find_bubble(self, bubble_id: int) -> Optional[Bubble]:
        for bubble in self.bubbles:
            if bubble.id == bubble_id:
                return bubble
        return None

    def attach_resources(self, bubble: Bubble, resources: List[Dict[str, str]]) -> None:
        bubble.resources.extend(resources)
        self.save()


class InfoFetcher:
    @staticmethod
    def fetch(query: str) -> List[Dict[str, str]]:
        """Fetch quick info using DuckDuckGo Instant Answer API.

        Network calls can fail in offline environments; failures are handled gracefully
        with a simple fallback message.
        """
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            fallback = {
                "title": "网络请求失败",
                "url": "",
                "snippet": f"未能获取在线资料：{exc}",
            }
            return [fallback]

        data = response.json()
        topics = data.get("RelatedTopics", [])
        results: List[Dict[str, str]] = []
        for topic in topics:
            if isinstance(topic, dict):
                text = topic.get("Text")
                first_url = topic.get("FirstURL")
                if text and first_url:
                    results.append({"title": text, "url": first_url, "snippet": text})
            # Some items may have nested topics
            subtopics = topic.get("Topics") if isinstance(topic, dict) else []
            for sub in subtopics or []:
                text = sub.get("Text")
                first_url = sub.get("FirstURL")
                if text and first_url:
                    results.append({"title": text, "url": first_url, "snippet": text})
        if not results:
            results.append({
                "title": "未找到相关信息",
                "url": "",
                "snippet": "没有返回相关主题，换个关键词试试。",
            })
        return results[:5]


def render_bubble(bubble: Bubble) -> str:
    lines = [
        f"Bubble #{bubble.id}: {bubble.title}",
        f"创建时间: {bubble.created_at}",
        "想法:",
        textwrap.indent(textwrap.fill(bubble.idea, width=70), prefix="  "),
        "资料:",
    ]
    if bubble.resources:
        for idx, resource in enumerate(bubble.resources, start=1):
            snippet = textwrap.fill(resource.get("snippet", ""), width=70)
            lines.append(f"  {idx}. {resource.get('title')}")
            lines.append(textwrap.indent(snippet, prefix="     "))
            if resource.get("url"):
                lines.append(f"     链接: {resource['url']}")
    else:
        lines.append("  暂无资料。使用选项 3 获取网络资讯。")
    return "\n".join(lines)


def prompt(msg: str) -> str:
    return input(f"{msg}: ").strip()


def main() -> None:
    manager = BubbleManager()
    print("欢迎来到 Bubble 实验室 — 记录想法、收集资料。\n")
    while True:
        print("请选择操作：")
        print(" 1. 查看已有 Bubbles")
        print(" 2. 为新想法创建 Bubble")
        print(" 3. 为 Bubble 获取网上资讯")
        print(" 4. 退出")
        choice = input(">> ").strip()

        if choice == "1":
            if not manager.bubbles:
                print("目前还没有 bubble，先创建一个吧！\n")
                continue
            for bubble in manager.bubbles:
                print(render_bubble(bubble))
                print("-" * 50)
        elif choice == "2":
            title = prompt("给这个想法取个标题")
            idea = prompt("描述你的想法")
            bubble = manager.create_bubble(title, idea)
            print(f"已创建 Bubble #{bubble.id}\n")
        elif choice == "3":
            if not manager.bubbles:
                print("还没有 bubble，先创建一个吧！\n")
                continue
            try:
                bubble_id = int(prompt("输入要更新的 Bubble 编号"))
            except ValueError:
                print("编号必须是数字。\n")
                continue
            bubble = manager.find_bubble(bubble_id)
            if not bubble:
                print("未找到对应 Bubble。\n")
                continue
            query = prompt("为这个想法检索什么关键词")
            resources = InfoFetcher.fetch(query)
            manager.attach_resources(bubble, resources)
            print("已为该 Bubble 添加资料：")
            print(render_bubble(bubble))
            print()
        elif choice == "4":
            print("再见！")
            break
        else:
            print("未识别的选项，请重试。\n")


if __name__ == "__main__":
    main()
