# Cantonese Salted Egg Yolk Mooncake · 40s TikTok/Reels

## 交付物

- **`Cantonese_SaltedEggYolk_Mooncake_40s.mp4`** — 1080×1920 / 30fps / 40.000s / H.264+AAC / ~30.8MB
- **`Cantonese_SaltedEggYolk_Mooncake_40s.srt`** — 烧录字幕文本（备用）
- **`CREDITS.md`** — 静态素材署名（CC 协议）
- **`build.py`** — 构建脚本（可重跑/微调）
- **`../preview/check_sheet.jpg`** — 7 段关键帧联系表

## 现状说明

你选的是 **「生成完整成片（消耗积分）」**。执行中视频生成模型 `kling-v3-t2v` 服务端返回 `route config not found`，6 段 AI 视频片段 + 1 次重试均失败，**该通道当前在沙箱里不可用**。

为不空跑交付，改为**预览级（previz）方案**：用 Wikimedia Commons 公共授权实拍月饼/灯笼/茶壶静态图，配 7 段慢推 Ken Burns + 暖色调 + 暗角，再按原脚本烧录字幕 + 合成 40 秒五声音阶背景乐。**这不是 AI 生成的电影质感镜头，但节拍、字幕、时长、版式都完全对齐你的脚本**——可直接用于验证节奏与文案，或者作为拍摄参考。

## 视频模型恢复后，如何换回 AI 电影质感镜头

`build.py` 把每个镜头参数化在 `SHOTS` 列表里。把每段 `render_shot(...)` 改为调用 `VideoGen`（每段约 50–100 积分），再让最终 ffmpeg 拼接/烧字幕/混音即可。示例伪代码：

```python
# 替换 render_shot() 内部为：
import openai  # 或对应的视频生成客户端
clip = generate_video(
    prompt=SCENE_PROMPTS[prefix],
    aspect_ratio="9:16", seconds=int(dur), resolution="1080P",
    output_dir=f"/tmp/mooncake_build/ai_clips",
)
# 然后让 concat_list 指向这些 .mp4
```

## 节拍 / 字幕时间轴

| 段 | 时间 | 画面 | 字幕（底部） |
|---|---|---|---|
| S1 | 0:00 – 0:04 | 掰开月饼露出金黄蛋黄（顶闪金标） | "Ever seen a snack that tastes like the full moon?" |
| S2 | 0:04 – 0:11 | 慢推月饼顶部雕花 | "Look at these stunning handcrafted patterns on the golden crust!" → "This is a classic Cantonese mooncake." |
| S3 | 0:11 – 0:19 | 切面：莲蓉裹蛋黄 | "Inside, silky sweet lotus paste hugs a rich salted egg yolk — just like the glowing full moon." |
| S4 | 0:19 – 0:27 | 红灯笼夜景 | "It's enjoyed for Mid-Autumn Festival, a special holiday all about family reunion." |
| S5a | 0:27 – 0:30.5 | 月饼剖面 | "It's rich and sweet!" |
| S5b | 0:30.5 – 0:34 | 茶壶（弹窗 "Pair with hot tea!"） | "Pro tip: Sip hot tea alongside to balance the sweetness!" |
| S6 | 0:34 – 0:40 | 月饼 hero（顶出系列名） | "Sweet, savory, and full of meaning — a bite of Chinese moon festival magic!" |

## 配乐说明

本片**未带可商用版权音乐**。自动合成的配乐只是占位，**正式发布前请替换为有授权的曲目**，例如：
- Pixabay Music（CC0）：搜 "guzheng soft" / "traditional chinese"
- Artlist / Epidemic Sound（订阅制）
- TikTok/Reels 内置音频库

**占位配乐构成**（`build.py` 内合成，AAC 128k / 44.1kHz 单声道）：
- 旋律层：D 大调五声音阶古筝式拨弦，0.6s 一拍，乐句循环铺满全程 40s；隔段升高八度避免单调，每 4 拍带弱拍装饰音
- 低频层：D3（146.83Hz）持续音垫全程托底 + 每 8 拍的低八度根音
- 电平：0.8s 淡入 / 0.9s 淡出，峰值归一化到 0.92。实测 0–39s 每秒 RMS 稳定在 0.155–0.251（动态差 4.2dB），无中途掉电平

> 修复记录：初版乐句仅 16 个音符（9.6s）就弹完，导致 9.6s 之后旋律层消失、只剩底噪般低音垫（电平暴跌约 13dB）。现已改为循环铺满全曲。

## 重新构建

```bash
python3 /workspace/mooncake/build.py
```

构建约 40 秒，产物落在 `/workspace/mooncake/output/`。
