#!/usr/bin/env python3
"""Transcript extraction for claude-youtube, via yt-dlp. Standard library only
(yt-dlp itself is a separate install: pipx install yt-dlp).

    python3 fetch_transcript.py https://www.youtube.com/watch?v=VIDEO_ID
    python3 fetch_transcript.py VIDEO_ID --lang en --format timed
    python3 fetch_transcript.py VIDEO_ID --format json --out t.json
    python3 fetch_transcript.py --file captions.vtt        # parse a file you already have
    python3 fetch_transcript.py --file captions.srt --format timed

It downloads captions only (never the video), prefers captions the creator
uploaded over YouTube's automatic ones, strips the timing tags, and removes
the rolling duplicate lines automatic captions are full of.

Output formats:

    text    one paragraph per pause, no timestamps (default)
    timed   [mm:ss] at the start of each ~30 second block, for hook and
            pacing analysis
    json    cues with start and end seconds, plus word count and words per
            minute

Use it on your own videos, or to study a video's structure for research. A
transcript is the creator's work: summarise and learn from it, do not
republish it. For your own uploads the official route is the Data API's
captions.download (200 units, OAuth); export from YouTube Studio is free.
"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

VIDEO_ID = re.compile(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([\w-]{11})|^([\w-]{11})$")
TS = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})")
CUE_TIME = re.compile(r"^\s*(\S+)\s+-->\s+(\S+)")
TAG = re.compile(r"<[^>]+>")


class TranscriptError(Exception):
    pass


def video_id(ref):
    m = VIDEO_ID.search(ref.strip())
    if not m:
        raise TranscriptError("cannot find a video id in %r" % ref)
    return m.group(1) or m.group(2)


def seconds(ts):
    m = TS.search(ts)
    if not m:
        raise ValueError("bad timestamp %r" % ts)
    h, mi, s, ms = m.groups()
    return int(h or 0) * 3600 + int(mi) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000.0


def clock(sec):
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return "%d:%02d:%02d" % (h, m, s) if h else "%02d:%02d" % (m, s)


def parse_captions(text):
    """Parse WebVTT or SRT into [{'start','end','text'}], de-duplicated.

    Automatic captions repeat each line as it scrolls: cue n shows line A,
    cue n+1 shows A then B. Only text not already emitted is kept.
    """
    cues = []
    block = []
    for raw in text.replace("\r\n", "\n").split("\n") + [""]:
        line = raw.strip()
        if line:
            block.append(line)
            continue
        if not block:
            continue
        timing = None
        body = []
        for b in block:
            m = CUE_TIME.match(b)
            if m and timing is None:
                timing = (seconds(m.group(1)), seconds(m.group(2)))
            elif timing is not None:
                body.append(b)
        block = []
        if timing is None:
            continue  # WEBVTT header, NOTE, STYLE, or an SRT index alone
        lines = [re.sub(r"\s+", " ", TAG.sub("", b)).strip() for b in body]
        lines = [ln for ln in lines if ln]
        if lines:
            cues.append({"start": timing[0], "end": timing[1], "lines": lines})
    out = []
    recent = []
    for c in cues:
        new = [ln for ln in c["lines"] if ln not in recent]
        recent = (recent + c["lines"])[-4:]
        if not new:
            continue
        txt = " ".join(new)
        if out and out[-1]["text"] == txt:
            continue
        out.append({"start": round(c["start"], 2), "end": round(c["end"], 2), "text": txt})
    return out


def to_text(cues, pause=2.0):
    paras, cur, last_end = [], [], None
    for c in cues:
        if cur and last_end is not None and c["start"] - last_end > pause:
            paras.append(" ".join(cur))
            cur = []
        cur.append(c["text"])
        last_end = c["end"]
    if cur:
        paras.append(" ".join(cur))
    return "\n\n".join(paras) + "\n"


def to_timed(cues, block=30):
    out, cur, start = [], [], None
    for c in cues:
        if start is None:
            start = c["start"]
        if c["start"] - start >= block and cur:
            out.append("[%s] %s" % (clock(start), " ".join(cur)))
            cur, start = [], c["start"]
        cur.append(c["text"])
    if cur:
        out.append("[%s] %s" % (clock(start), " ".join(cur)))
    return "\n".join(out) + "\n"


def stats(cues):
    words = sum(len(c["text"].split()) for c in cues)
    span = (cues[-1]["end"] - cues[0]["start"]) if cues else 0
    return {"words": words, "duration_seconds": round(span, 1),
            "words_per_minute": round(words / (span / 60.0), 1) if span else None,
            "first_30s_words": sum(len(c["text"].split()) for c in cues if c["start"] < 30)}


def download(ref, lang="en"):
    exe = shutil.which("yt-dlp")
    if not exe:
        raise TranscriptError("yt-dlp is not installed. Install it (pipx install yt-dlp) or "
                              "export captions from YouTube Studio and use --file.")
    vid = video_id(ref)
    with tempfile.TemporaryDirectory() as tmp:
        for auto in (False, True):
            cmd = [exe, "--skip-download", "--no-playlist", "--sub-format", "vtt",
                   "--sub-langs", "%s.*,%s" % (lang, lang),
                   "--write-auto-subs" if auto else "--write-subs",
                   "-o", os.path.join(tmp, "%(id)s.%(ext)s"),
                   "https://www.youtube.com/watch?v=%s" % vid]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            files = sorted(glob.glob(os.path.join(tmp, "*.vtt")))
            if files:
                with open(files[0], encoding="utf-8") as fh:
                    return vid, ("automatic" if auto else "uploaded"), fh.read()
        raise TranscriptError("no %s captions for %s. yt-dlp said: %s"
                              % (lang, vid, (proc.stderr or proc.stdout).strip()[-400:]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("video", nargs="?", help="video URL or id")
    ap.add_argument("--file", help="parse a local .vtt or .srt instead of downloading")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--format", default="text", choices=["text", "timed", "json"])
    ap.add_argument("--block", type=int, default=30, help="seconds per block for --format timed")
    ap.add_argument("--out", help="write here instead of stdout")
    args = ap.parse_args(argv)
    try:
        if args.file:
            with open(args.file, encoding="utf-8") as fh:
                raw, vid, kind = fh.read(), None, "file"
        elif args.video:
            vid, kind, raw = download(args.video, args.lang)
        else:
            ap.error("give a video URL or id, or --file")
        cues = parse_captions(raw)
    except (TranscriptError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print("fetch_transcript: %s" % exc, file=sys.stderr)
        return 2
    if not cues:
        print("fetch_transcript: no caption text found", file=sys.stderr)
        return 2
    if args.format == "json":
        text = json.dumps({"video_id": vid, "captions": kind, "stats": stats(cues), "cues": cues}, indent=2) + "\n"
    elif args.format == "timed":
        text = to_timed(cues, args.block)
    else:
        text = to_text(cues)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s (%s captions, %d words)" % (args.out, kind, stats(cues)["words"]), file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
