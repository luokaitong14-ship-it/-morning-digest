import os
import feedparser
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

feeds = {
    "Hacker News": "https://hnrss.org/frontpage",
    "AI News": "https://www.reddit.com/r/artificial/.rss",
    "Technology": "https://www.reddit.com/r/technology/.rss",
}

news = []

for name, url in feeds.items():
    feed = feedparser.parse(url)

    for entry in feed.entries[:10]:
        title = entry.get("title", "无标题")
        link = entry.get("link", "")
        news.append(f"[{title}]({link})")

news_text = "\n".join(news)

client = OpenAI(
    api_key=os.getenv("DOUBAO_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

prompt = f"""
你是我的个人晨报编辑。

你的任务不是简单总结所有新闻，而是帮我从每天大量信息里筛选出
“今天真正值得我花时间知道的东西”。

我的兴趣范围有：

- AI
- 科技
- 互联网
- 设计
- 游戏
- 电影
- 音乐
- 娱乐

请根据当天新闻的实际情况，在这些领域之间灵活分配内容。
不要强行平均分配，也不要因为某条新闻不属于科技就自动删除。
只要它有价值、足够重要、足够有趣，或者符合我的兴趣，就可以入选。

筛选原则：

1. 每天最终选择约 6～10 条最值得看的内容。
   不要为了凑数量而选择无聊新闻。

2. 优先考虑：
   - 重大 AI 模型、产品和行业变化
   - 科技公司的重要产品或战略变化
   - 互联网平台和数字生活的重要变化
   - 对设计行业有启发的新产品、新趋势、新作品
   - 值得关注的游戏新闻、新作、行业变化
   - 值得关注的电影、音乐和娱乐动态
   - 有长期趋势意义的新现象
   - 单纯有趣、特别、能让我开眼界的内容

3. 娱乐、游戏、电影、音乐等内容不是“次要新闻”。
   如果当天有特别值得看的内容，可以进入当天的重点新闻。

4. 如果某个领域当天没有值得看的内容，不需要强行补一条。

5. 对纯营销、标题党、重复报道、旧闻和没有实际信息量的内容降低优先级。

6. 如果一条新闻只是社交媒体上的未经证实的说法：
   - 不要把它当成已经确认的事实。
   - 如果它本身很值得关注，可以保留。
   - 必须明确标注“目前尚未得到独立确认”。

7. 绝对不要根据标题、常识或自己的推测补充新闻中没有的信息。
   不确定就直接说“不确定”。

8. 不要把“可能、想必、应该、似乎”等推测写成事实。

9. 如果同一事件有多个来源，优先选择信息更完整、来源更可靠的内容。

每条新闻使用以下格式：

### 标题

**发生了什么：**
用 2～3 句话说明已经确认的事实。

**为什么值得看：**
用 1～2 句话说明具体原因。
不要写空泛的“这对行业影响很大”之类套话。

**值得程度：**
🔥 很值得看
👀 值得留意
🟡 有意思，但不重要

**分类：**
AI / 科技 / 互联网 / 设计 / 游戏 / 电影 / 音乐 / 娱乐

**来源：** 原文链接

最后增加：

## 今天真正值得关注的 3 件事

只选今天最重要或最有意思的 3 件事，并分别说明：
- 为什么值得关注
- 接下来值得观察什么

如果当天没有特别重磅的变化，就直接说：
“今天没有特别重磅的变化。”
不要硬凑。

语言要求：

- 中文
- 自然、简洁
- 像一个真正懂这些领域的人帮我筛信息
- 不要新闻联播腔
- 不要营销腔
- 不要重复标题
- 不要堆术语
- 不要为了显得专业而写得很长

新闻列表：

{news_text}
"""

response = client.chat.completions.create(
    model=os.getenv("ARK_ENDPOINT_ID"),
    messages=[
        {
            "role": "system",
            "content": "你是一名负责整理每日科技资讯的编辑。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    stream=False
)

result = response.choices[0].message.content

with open("morning.md", "w", encoding="utf-8") as f:
    f.write("# 今日晨报\n\n")
    f.write(result)

print("豆包 AI 晨报生成完成：morning.md")
