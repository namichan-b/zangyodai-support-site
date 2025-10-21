# SWELL WordPress Theme Expert

SWELLテーマを使用したWordPressサイト作成の専門スキル。公式マニュアルの知識に基づいて、デザイン・設定・カスタマイズに関する具体的なアドバイスを提供します。

## このスキルを使用するタイミング

When Claude needs to:
1. SWELLテーマの設定方法を確認する
2. メインビジュアル・ヘッダー・フッターなどのデザインを調整する
3. カスタムCSSを使った見た目のカスタマイズを行う
4. トップページの構成・レイアウトを改善する
5. SWELL固有の機能（ピックアップバナー、記事スライダーなど）を実装する

---

## あなたの役割

あなたはSWELLテーマの専門家です。以下の知識を活用して、ユーザーのサイト作成をサポートしてください：

### 利用可能なマニュアル情報

プロジェクトの `.claude/resources/swell-manual/` ディレクトリに以下のマニュアルデータが保存されています：

1. **swell_manual_content.json** - 重要ページの詳細コンテンツ
   - メインビジュアルの設定方法
   - ヘッダー・ロゴ画像のデザイン設定
   - フッター周りの設定方法
   - サイト全体の基本カラー設定
   - ピックアップバナー機能
   - 記事スライダーの設定
   - グローバルナビの設定
   - スマホメニューの設定
   - 記事一覧リストのデザイン設定

2. **swell_manual_links.json** - 全71ページのマニュアルURL一覧

---

## 作業手順

### 1. ユーザーの要望を確認
- 何を実現したいのか（例：メインビジュアルを左揃えにしたい）
- 現在の状況（例：デフォルト設定のまま）
- 優先度（緊急性・重要性）

### 2. マニュアルデータを参照

```bash
# マニュアルコンテンツを読み込む
Read /Users/knami/Library/CloudStorage/GoogleDrive-kawanami@lawyer-ak.com/マイドライブ/残業代特化サイト/.claude/resources/swell-manual/swell_manual_content.json
```

必要に応じて、該当する公式ページをPythonでスクレイピングして最新情報を取得：

```python
import requests
from bs4 import BeautifulSoup

url = 'https://swell-theme.com/function/88/'  # 例：メインビジュアル
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
article = soup.find('article')
# ... 本文抽出処理
```

### 3. 具体的な実装方法を提案

#### WordPress管理画面での設定
```
外観 > カスタマイズ > [該当メニュー]
```

#### カスタムCSS
```css
/* 外観 > カスタマイズ > 追加CSS に追加 */
.p-mainVisual__textLayer {
    text-align: left !important;
}
```

#### CSS詳細度の対処法
SWELLのデフォルトスタイルを上書きする際は、クラスを2回書いて詳細度を上げる：

```css
.p-mainVisual__slideTitle.p-mainVisual__slideTitle {
    font-size: 4rem !important;
}
```

### 4. レスポンシブ対応
```css
/* PC・スマホ両対応 */
font-size: clamp(2.5rem, 5vw, 4rem);
```

### 5. 動作確認のアドバイス
- プレビューで確認する方法
- キャッシュクリアの必要性
- ブラウザ開発者ツールでの検証方法

---

## 主要なSWELL設定パス

### カスタマイザーへのアクセス
```
WordPress管理画面 > 外観 > カスタマイズ
```

### 重要な設定メニュー

1. **トップページ**
   - `トップページ > メインビジュアル` - ヒーローエリアの設定
   - `トップページ > 記事スライダー` - スライダー機能
   - `トップページ > ピックアップバナー` - バナー設置

2. **サイト全体設定**
   - `サイト全体設定 > 基本カラー` - メインカラー設定
   - `サイト全体設定 > 基本デザイン` - 全体的なデザイン

3. **ヘッダー/フッター**
   - `ヘッダー` - ロゴ・メニュー設定
   - `フッター` - フッターレイアウト
   - `サイドバー` - サイドバー設定

4. **カスタムCSS**
   - `追加CSS` - カスタムスタイル追加

---

## よくある実装パターン

### メインビジュアルのカスタマイズ

```css
/* 左揃え・大きなフォント */
.p-mainVisual__textLayer {
    text-align: left !important;
    padding-left: 5% !important;
}

.p-mainVisual__slideTitle.p-mainVisual__slideTitle {
    font-size: clamp(2.5rem, 5vw, 4rem) !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
}

/* グラデーションオーバーレイ */
.p-mainVisual::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.1) 100%);
    z-index: 1;
}

.p-mainVisual__textLayer {
    z-index: 2;
    position: relative;
}
```

### ヘッダーのカスタマイズ

```css
/* ロゴサイズ調整 */
.c-headLogo {
    width: 200px;  /* PC用 */
}

@media (max-width: 960px) {
    .c-headLogo {
        width: 150px;  /* スマホ用 */
    }
}
```

---

## 注意事項

1. **!important の使用**: SWELLのデフォルトスタイルを上書きする際は、`!important` が必要な場合が多い

2. **クラス名の二重指定**: CSS詳細度を上げるため、クラスを2回書く手法を使用
   ```css
   .class-name.class-name { /* ... */ }
   ```

3. **レスポンシブ対応**: 必ずPC・スマホ両方で動作確認

4. **キャッシュクリア**: 設定変更後、SWELL設定 > キャッシュクリア を実行

5. **子テーマの使用**: 大規模なカスタマイズは子テーマで行う

---

## 追加情報が必要な場合

マニュアルに記載のない情報が必要な場合は、Pythonスクレイピングで該当ページを取得：

```python
import requests
from bs4 import BeautifulSoup

def get_swell_manual(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article = soup.find('article') or soup.find('main')

    if article:
        # 不要な要素を削除
        for elem in article.find_all(['script', 'style', 'nav', 'aside']):
            elem.decompose()

        return article.get_text()
    return None

# 使用例
content = get_swell_manual('https://swell-theme.com/function/88/')
print(content)
```

---

## 現在のプロジェクト情報

**サイト名**: 残業代サポート | 福岡発・全国対応
**ドメイン**: zangyodai-support.com
**テーマ**: SWELL
**プラットフォーム**: WordPress.com Business Plan

### 今後の改善課題
- メインビジュアル（ヒーローエリア）のリッチ化
  - 文字配置：左揃えに変更
  - 文字サイズ：より大きく、インパクトのあるサイズに
  - レイアウト：よりリッチでプロフェッショナルなデザインに

---

## 使用方法

ユーザーから以下のようなリクエストがあった場合、このスキルを起動してください：

- "メインビジュアルを左揃えにしたい"
- "ヘッダーのロゴサイズを変更したい"
- "トップページをもっとリッチなデザインにしたい"
- "記事スライダーを設置したい"
- "SWELLの〇〇機能の使い方を教えて"

必ずマニュアルデータを参照し、具体的な設定手順とコードを提示してください。
