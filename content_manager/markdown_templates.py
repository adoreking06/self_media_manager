import re
from pathlib import Path
from typing import Dict, List

from .config import TEMPLATES_DIR
from .models import Topic


def safe_filename(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "_", value)
    value = re.sub(r"\s+", "_", value.strip())
    return value[:80] or "untitled"


def platform_body(platform: str, topic: Topic) -> str:
    common_header = f"""# {topic.title}

- 选题ID：{topic.topic_id}
- 主题：{topic.theme}
- 内容线：{topic.content_line}
- 目标平台：{platform}
- 当前状态：{topic.status}
- 计划发布时间：{topic.publish_date or "待定"}

"""

    platform_sections: Dict[str, str] = {
        "小红书": """## 封面标题

> 控制在 18 字以内，突出身份、进度或反差。

## 开头钩子

- 我是谁：
- 我遇到的问题：
- 这篇能帮读者带走什么：

## 正文结构

1. 背景：为什么做这个选题？
2. 过程：我具体做了什么？
3. 方法：可复用的步骤/资料/工具。
4. 反思：本周最大的收获或坑。

## 图文素材清单

- 封面截图/自拍/学习记录：
- 过程图：
- 总结图：

## 标签

#吉大AI #AI本科生 #科研入门 #CS自学 #港校申请

## 发布前检查

- [ ] 标题像真人说话，不像论文题目
- [ ] 第一屏有具体问题或成果
- [ ] 至少一张图能单独传达信息
""",
        "B站": """## 视频标题

> 标题可以更完整，突出阶段性记录或经验总结。

## 视频简介

- 本期主题：
- 适合谁看：
- 相关资料/课程/论文：

## 视频大纲

| 时间段 | 内容 |
| --- | --- |
| 00:00-00:20 | 开场：身份 + 本期问题 |
| 00:20-02:00 | 背景：为什么做这件事 |
| 02:00-06:00 | 主体：过程、方法、材料 |
| 06:00-08:00 | 反思：收获、踩坑、下一步 |

## 口播草稿

大家好，我是吉大 AI 本科生。今天想记录一下：

## 素材清单

- 屏幕录制：
- 代码/笔记截图：
- 课程或论文截图：
- 健身/生活 B-roll：

## 发布前检查

- [ ] 前 20 秒讲清楚为什么值得看
- [ ] 简介里放资料链接或关键词
- [ ] 封面有明确对象：课程/论文/申请/训练
""",
        "抖音": """## 3 秒钩子

> 用一句话让用户知道：这条和我有什么关系？

## 15-60 秒脚本

| 镜头 | 画面 | 字幕/口播 |
| --- | --- | --- |
| 1 | 近景/桌面/训练画面 | 我是吉大 AI 本科生，这周我在做： |
| 2 | 笔记/代码/论文/申请表 | 最大的问题是： |
| 3 | 过程快剪 | 我用了这几个步骤： |
| 4 | 总结画面 | 如果你也在准备，可以先从这里开始： |

## 字幕关键词

- 吉大AI本科生
- 科研入门
- CS自学
- 多模态论文
- 港校申请

## 发布前检查

- [ ] 前 3 秒有明确冲突或结果
- [ ] 字幕足够大，静音也能看懂
- [ ] 结尾有一个轻量互动问题
""",
    }

    return common_header + platform_sections[platform]


def generate_templates(topic: Topic, output_dir: Path = TEMPLATES_DIR) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    for platform in topic.platform_list():
        filename = f"{topic.topic_id}_{safe_filename(platform)}_{safe_filename(topic.title)}.md"
        path = output_dir / filename
        path.write_text(platform_body(platform, topic), encoding="utf-8")
        paths.append(path)

    return paths
