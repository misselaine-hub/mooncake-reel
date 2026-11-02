#!/usr/bin/env python3
"""构建 40 秒 9:16 月饼短视频（previz 版）。"""
import os
import subprocess
import wave
import numpy as np

ROOT = "/workspace/mooncake"
ASSETS = f"{ROOT}/assets"
OUT = f"{ROOT}/output"
TMP = "/tmp/mooncake_build"
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
W, H, FPS = 1080, 1920, 30
SR = 44100
TOTAL = 40.0

os.makedirs(TMP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# (输出前缀, 素材, 时长秒, 缩放速率)
SHOTS = [
    ("shot01", "shot01_crack.jpg",    4.0, 0.0009),
    ("shot02", "shot02_pattern.jpg",  7.0, 0.0006),
    ("shot03", "shot03_cross.jpg",    8.0, 0.0008),
    ("shot04", "shot04_festival.jpg", 8.0, 0.0005),
    ("shot05", "shot05_bite.jpg",     3.5, 0.0010),
    ("shot06", "shot06_tea.jpg",      3.5, 0.0008),
    ("shot07", "shot07_hero.jpg",     6.0, 0.0008),
]

def render_shot(prefix, img, dur, zoom_rate):
    inp = f"{ASSETS}/{img}"
    out = f"{TMP}/{prefix}.mp4"
    if os.path.exists(out) and os.path.getsize(out) > 20000:
        print(f"  [skip] {prefix} (cached)")
        return out
    d = int(round(dur * FPS))
    z_expr = f"min(zoom+{zoom_rate},1.10)"
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        f"zoompan=z='{z_expr}':d={d}:s={W}x{H}:fps={FPS},"
        f"hue=s=1.08,colorbalance=rs=0.05:gs=0.02:bs=-0.05,"
        f"vignette=0.34,format=yuv420p"
    )
    # -t 放在 -i 之后做输出时长；-frames:v 硬封顶防 zoompan 失控
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-i", inp,
        "-t", f"{dur}",
        "-vf", vf, "-r", str(FPS),
        "-frames:v", str(d),
        "-c:v", "libopenh264",
        "-rc_mode", "1", "-b:v", "5M", "-maxrate", "5M", "-bufsize", "10M",
        "-allow_skip_frames", "1",
        "-g", "60", "-bf", "0",
        "-pix_fmt", "yuv420p", out,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        raise RuntimeError(f"{prefix} 渲染失败: {r.stderr[-500:]}")
    print(f"  [ok]   {prefix} ({dur}s, {os.path.getsize(out)//1024}KB)")
    return out

print("[1/4] 渲染 7 段镜头…")
for s in SHOTS:
    render_shot(*s)

# 拼接
concat_list = f"{TMP}/concat.txt"
with open(concat_list, "w") as f:
    for s in SHOTS:
        f.write(f"file '{TMP}/{s[0]}.mp4'\n")
concat_mp4 = f"{TMP}/concat.mp4"
print("[2/4] 拼接…")
r = subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-f", "concat", "-safe", "0", "-i", concat_list,
    "-c", "copy", concat_mp4,
], capture_output=True, text=True)
if r.returncode != 0:
    raise RuntimeError(f"拼接失败: {r.stderr[-400:]}")
print(f"  [ok]   concat.mp4 ({os.path.getsize(concat_mp4)//1024}KB)")

# ASS 字幕
def hms(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t - h*3600 - m*60
    return f"{h:d}:{m:02d}:{s:05.2f}"

COL_WHITE = "&H00FFFFFF"
COL_GOLD  = "&H0079D4FF"
COL_BLACK = "&H00000000"
COL_BOX   = "&H80000000"

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Noto Sans,58,{COL_WHITE},{COL_BLACK},&H00111111,{COL_BOX},-1,0,0,0,100,100,0,0,1,4,2,2,60,60,220,1
Style: Flash,Noto Sans,34,{COL_GOLD},{COL_BLACK},&H00111111,&H00000000,-1,0,0,0,100,100,0,0,1,3,2,8,80,80,220,1
Style: Pop,Noto Sans,52,{COL_GOLD},{COL_BLACK},&H00111111,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,60,60,200,1
Style: Series,Noto Sans,42,{COL_WHITE},{COL_BLACK},&H00111111,&H00000000,-1,0,0,0,100,100,0,0,1,3,2,8,60,60,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{hms(0.30)},{hms(3.70)},Caption,,0,0,0,,Ever seen a snack that tastes like the full moon?
Dialogue: 0,{hms(0.20)},{hms(3.20)},Flash,,0,0,0,,HAVE YOU TRIED THIS ICONIC CHINESE FESTIVAL TREAT?
Dialogue: 0,{hms(4.30)},{hms(7.40)},Caption,,0,0,0,,Look at these stunning handcrafted patterns on the golden crust!
Dialogue: 0,{hms(7.50)},{hms(10.80)},Caption,,0,0,0,,This is a classic Cantonese mooncake.
Dialogue: 0,{hms(11.30)},{hms(18.80)},Caption,,0,0,0,,Inside, silky sweet lotus paste hugs a rich salted egg yolk — just like the glowing full moon.
Dialogue: 0,{hms(19.30)},{hms(26.80)},Caption,,0,0,0,,It's enjoyed for Mid-Autumn Festival, a special holiday all about family reunion.
Dialogue: 0,{hms(27.30)},{hms(30.30)},Caption,,0,0,0,,It's rich and sweet!
Dialogue: 0,{hms(30.80)},{hms(33.80)},Caption,,0,0,0,,Pro tip: Sip hot tea alongside to balance the sweetness!
Dialogue: 0,{hms(30.60)},{hms(33.60)},Pop,,0,0,0,,Pair with hot tea!
Dialogue: 0,{hms(34.30)},{hms(39.80)},Caption,,0,0,0,,Sweet, savory, and full of meaning — a bite of Chinese moon festival magic!
Dialogue: 0,{hms(36.00)},{hms(40.00)},Series,,0,0,0,,Traditional Chinese Snacks
"""
ass_path = f"{TMP}/captions.ass"
with open(ass_path, "w") as f:
    f.write(ass)
print(f"  [ok]   captions.ass")

# 配乐（五声音阶古筝拨弦 + 持续低音垫）
def pluck(freq, dur, sr=SR, decay=2.6, bright=1.0):
    t = np.linspace(0, dur, int(sr*dur), endpoint=False)
    env = np.exp(-t * decay)
    env *= np.minimum(1.0, t * 150 + 0.05)
    sig = (np.sin(2*np.pi*freq*t)
           + 0.35*bright*np.sin(2*np.pi*freq*2*t)
           + 0.18*bright*np.sin(2*np.pi*freq*3*t))
    return sig * env * 0.6

def pad(freq, dur, sr=SR):
    t = np.linspace(0, dur, int(sr*dur), endpoint=False)
    sig = np.sin(2*np.pi*freq*t) + 0.4*np.sin(2*np.pi*freq*1.5*t)
    lfo = 0.88 + 0.12*np.sin(2*np.pi*0.15*t)   # 起伏减弱，避免段落性掉电平
    return sig * 0.30 * lfo

# D 大调五声音阶，跨两个八度
NOTES = [293.66, 329.63, 369.99, 440.00, 493.88, 587.33, 659.25, 739.99]
phrase = [0,2,4,2, 1,3,5,3, 2,4,6,4, 5,3,2,0]
beat = 0.6
# 关键修复：乐句循环铺满全曲（原实现 16 音 × 0.6s = 9.6s 后旋律消失）
audio = np.zeros(int(SR * (TOTAL + 2.5)))     # 多留 2.5s 容纳尾音，最后截断
for i in range(int(TOTAL / beat) + 6):
    start = i * beat
    bar = i // 16
    idx = phrase[i % len(phrase)]
    oct_boost = 2 if bar % 2 == 1 else 0      # 隔段升高，避免单调
    freq = NOTES[min(idx + oct_boost, len(NOTES) - 1)]
    accent = 1.0 if i % 4 == 0 else (0.80 if i % 2 == 0 else 0.64)
    n = pluck(freq, beat * 1.9, decay=2.4 if accent > 0.9 else 2.9)
    s = int(start * SR); e = s + len(n)
    if e > len(audio): break
    audio[s:e] += n * accent
    if i % 8 == 0:                             # 每 8 拍垫一个低八度根音
        b = pluck(NOTES[0] * 0.5, beat * 2.8, decay=1.7, bright=0.5)
        s2 = int(start * SR); e2 = s2 + len(b)
        if e2 <= len(audio):
            audio[s2:e2] += b * 0.55
    if i % 4 == 2:                             # 弱拍装饰音
        g = pluck(NOTES[min(idx + 4, len(NOTES) - 1)], beat * 1.2, decay=4.5, bright=0.8)
        s3 = int((start + beat * 0.5) * SR); e3 = s3 + len(g)
        if e3 <= len(audio):
            audio[s3:e3] += g * 0.30

audio = audio[:int(SR * TOTAL)]
audio += pad(146.83, TOTAL)                    # D3 持续音垫，全程托底
fade_in = int(0.8 * SR)
fade_out = int(0.9 * SR)
audio[:fade_in] *= np.linspace(0, 1, fade_in)
audio[-fade_out:] *= np.linspace(1, 0, fade_out)
impulse = np.zeros(21); impulse[0] = 1; impulse[2] = 0.35; impulse[4] = 0.15; impulse[6] = 0.08; impulse[8] = 0.04; impulse[10] = 0.02
audio = np.convolve(audio, impulse)[:len(audio)]
peak = float(np.abs(audio).max())
if peak > 0:
    audio = audio / peak * 0.92                 # 归一化，保证全程电平一致
print(f"  [ok]   BGM 峰值归一化 ({peak:.3f} -> 0.920)")

bgm_wav = f"{TMP}/bgm.wav"
pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
with wave.open(bgm_wav, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f"[3/4] BGM 合成 ({os.path.getsize(bgm_wav)//1024}KB)")

final_mp4 = f"{OUT}/Cantonese_SaltedEggYolk_Mooncake_40s.mp4"
subs_mp4 = f"{TMP}/with_subs.mp4"
# subtitles 滤镜路径需把 \ 与 : 转义；这里无 : 也要避免 shell 展开
escaped = ass_path.replace("\\", "\\\\").replace(":", "\\:")
r = subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-i", concat_mp4, "-vf", f"subtitles='{escaped}'",
    "-c:v", "libopenh264", "-b:v", "8M", "-pix_fmt", "yuv420p", subs_mp4,
], capture_output=True, text=True)
if r.returncode != 0:
    raise RuntimeError(f"烧字幕失败: {r.stderr[-600:]}")

r = subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-i", subs_mp4, "-i", bgm_wav,
    # 淡入淡出已在 wav 内完成，此处不再叠加 afade（避免尾部双重衰减到静音）
    "-filter_complex", "[1:a]volume=0.9,alimiter=limit=0.95[m]",
    "-map", "0:v", "-map", "[m]",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
    "-shortest", final_mp4,
], capture_output=True, text=True)
if r.returncode != 0:
    raise RuntimeError(f"混音失败: {r.stderr[-600:]}")

print(f"[4/4] 完成 → {final_mp4} ({os.path.getsize(final_mp4)//1024}KB)")
