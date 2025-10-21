#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SWELL テーマ公式マニュアル自動取得スクリプト

機能:
- サイトマップから /manual/ を含むURLを抽出
- フォールバックとして /manual/ インデックスからのリンク探索
- 各ページを取得し、HTMLと簡易テキストを保存
- 取得結果のインデックス (CSV/URLリスト) を出力

依存: 標準ライブラリのみ (外部パッケージ不要)
"""

from __future__ import annotations

import csv
import re
import sys
import time
import gzip
import argparse
import pathlib
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from typing import Iterable, List, Optional, Set, Tuple


DEFAULT_BASE = "https://swell-theme.com"
SITEMAP_INDEX_PATHS = [
    "/sitemap_index.xml",  # WordPress (Yoastなど)の一般的なインデックス
    "/sitemap.xml",        # 単一サイトマップの場合
]


class SimpleTextExtractor(HTMLParser):
    """記事本文の可能性が高い領域からテキストを抽出する簡易パーサ。

    - 優先: <article>, <main>, id="content" の <div>
    - 次点: <body>
    - 出力: 見出し、段落、リスト、表のセル、コードブロックを行単位で連結
    """

    TARGET_TAGS = {
        "p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "th", "td", "pre", "code", "blockquote"
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._stack: List[Tuple[str, dict]] = []
        self._capture_level: Optional[int] = None
        self._buffer: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attr_map = {k: (v or "") for k, v in attrs}
        self._stack.append((tag, attr_map))

        # 開始の判定
        if self._capture_level is None:
            if tag in ("article", "main"):
                self._capture_level = len(self._stack)
            elif tag == "div" and attr_map.get("id", "") == "content":
                self._capture_level = len(self._stack)

        # ターゲットブロックの開始で段落境界を入れる
        if self._capture_level is not None and tag in ("p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "blockquote"):
            self._buffer.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._stack:
            self._stack.pop()

        # キャプチャ領域終了
        if self._capture_level is not None and len(self._stack) < self._capture_level:
            self._capture_level = None

        # ブロック要素の終端で改行
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "blockquote", "tr"):
            self._buffer.append("\n")

    def handle_data(self, data: str) -> None:
        if self._capture_level is None:
            # フォールバック: 本文領域が一度も見つからない場合、<body> 全体を許容
            if any(t == "body" for t, _ in self._stack):
                text = data.strip()
                if text:
                    self._buffer.append(text)
            return

        text = data.strip()
        if not text:
            return

        # 現在のタグがテキスト抽出対象かを確認
        current_tag = self._stack[-1][0] if self._stack else ""
        if current_tag in self.TARGET_TAGS:
            self._buffer.append(text)

    def get_text(self) -> str:
        # 余分な空行を圧縮
        joined = " ".join(part for part in self._buffer)
        joined = re.sub(r"\s+\n", "\n", joined)
        joined = re.sub(r"\n{3,}", "\n\n", joined)
        return joined.strip()


def request_url(url: str, *, timeout: float = 30.0, retries: int = 3, backoff: float = 1.5) -> bytes:
    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                    ),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                },
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                encoding = resp.headers.get("Content-Encoding", "").lower()
                if encoding == "gzip":
                    try:
                        data = gzip.decompress(data)
                    except Exception:
                        pass
                return data
        except Exception as e:  # noqa: BLE001 - 低レイヤエラーをラップ
            last_err = e
            time.sleep(backoff ** (attempt + 1))
    assert last_err is not None
    raise last_err


def find_manual_urls_from_sitemaps(base_url: str) -> List[str]:
    manual_urls: List[str] = []
    checked: Set[str] = set()

    for path in SITEMAP_INDEX_PATHS:
        index_url = base_url.rstrip("/") + path
        try:
            raw = request_url(index_url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            raise
        except Exception:
            continue

        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            continue

        # サイトマップインデックス or 単一サイトマップを判定
        sitemap_tags = root.findall("{*}sitemap")
        if sitemap_tags:
            # 子サイトマップ列挙
            child_sitemaps = [elm.findtext("{*}loc") or "" for elm in sitemap_tags]
            for sm_url in child_sitemaps:
                if not sm_url or sm_url in checked:
                    continue
                checked.add(sm_url)
                try:
                    sm_raw = request_url(sm_url)
                    sm_root = ET.fromstring(sm_raw)
                except Exception:
                    continue
                for url_tag in sm_root.findall("{*}url"):
                    loc = (url_tag.findtext("{*}loc") or "").strip()
                    if "/manual/" in loc:
                        manual_urls.append(loc)
        else:
            # 単一サイトマップ
            for url_tag in root.findall("{*}url"):
                loc = (url_tag.findtext("{*}loc") or "").strip()
                if "/manual/" in loc:
                    manual_urls.append(loc)

    # 重複排除
    return sorted(dict.fromkeys(manual_urls))


def find_manual_urls_from_index(base_url: str) -> List[str]:
    index_url = base_url.rstrip("/") + "/manual/"
    try:
        raw = request_url(index_url)
    except Exception:
        return []

    html = raw.decode("utf-8", errors="ignore")
    # シンプルに /manual/ 配下へのリンクを拾う
    candidates = re.findall(r"href=\"(https?://[^\"]+/manual/[^\"]+)\"", html)
    # 同一ホストのみ
    host = re.match(r"https?://([^/]+)/", base_url + "/")
    allowed_host = host.group(1) if host else ""
    urls = []
    for u in candidates:
        if allowed_host and not u.startswith(f"https://{allowed_host}") and not u.startswith(f"http://{allowed_host}"):
            continue
        urls.append(u)
    return sorted(dict.fromkeys(urls))


def extract_title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    title = re.sub(r"\s+", " ", m.group(1)).strip()
    return title


def html_to_text(html: str) -> str:
    parser = SimpleTextExtractor()
    parser.feed(html)
    text = parser.get_text()
    if not text:
        # フォールバック: 全タグ除去の簡易テキスト
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
    return text


def sanitize_path_segment(text: str, max_len: int = 80) -> str:
    text = text.strip().replace("/", "-")
    text = re.sub(r"[^\w\-一-龯ぁ-んァ-ヶー・（）()\s]", "", text)
    text = re.sub(r"\s+", "_", text)
    if len(text) > max_len:
        text = text[:max_len].rstrip("_")
    return text or "page"


def save_page(output_dir: pathlib.Path, url: str, html_bytes: bytes) -> Tuple[pathlib.Path, pathlib.Path, str]:
    html = html_bytes.decode("utf-8", errors="ignore")
    title = extract_title(html)
    base_name = sanitize_path_segment(title or pathlib.PurePosixPath(urllib.parse.urlparse(url).path).name or "manual")
    html_path = output_dir / f"{base_name}.html"
    txt_path = output_dir / f"{base_name}.txt"

    html_path.write_text(html, encoding="utf-8")
    txt = html_to_text(html)
    txt_path.write_text(txt, encoding="utf-8")
    return html_path, txt_path, title


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="SWELL マニュアル自動取得")
    parser.add_argument("--base", default=DEFAULT_BASE, help="ベースURL (既定: https://swell-theme.com)")
    parser.add_argument("--out", default=str(pathlib.Path.cwd() / "SWELL_マニュアル"), help="保存先ディレクトリ")
    parser.add_argument("--delay", type=float, default=0.8, help="各リクエスト間の待機秒")
    parser.add_argument("--limit", type=int, default=0, help="取得上限 (0は無制限)")
    args = parser.parse_args(argv)

    base_url = args.base.rstrip("/")
    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    urls = find_manual_urls_from_sitemaps(base_url)
    if not urls:
        urls = find_manual_urls_from_index(base_url)

    if not urls:
        print("[ERROR] マニュアルのURLを検出できませんでした。", file=sys.stderr)
        return 1

    # 上限適用
    if args.limit > 0:
        urls = urls[: args.limit]

    urls_txt = out_dir / "urls.txt"
    urls_txt.write_text("\n".join(urls) + "\n", encoding="utf-8")

    index_csv = out_dir / "index.csv"
    with index_csv.open("w", encoding="utf-8", newline="") as fcsv:
        writer = csv.writer(fcsv)
        writer.writerow(["url", "html_path", "text_path", "title"])  # header

        for i, url in enumerate(urls, start=1):
            try:
                content = request_url(url)
            except Exception as e:
                print(f"[WARN] 取得失敗: {url} ({e})", file=sys.stderr)
                continue

            html_path, txt_path, title = save_page(out_dir, url, content)
            writer.writerow([url, str(html_path), str(txt_path), title])
            print(f"[{i}/{len(urls)}] saved: {title or url}")
            time.sleep(max(args.delay, 0.0))

    print(f"保存先: {out_dir}")
    print(f"URL一覧: {urls_txt}")
    print(f"インデックス: {index_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


