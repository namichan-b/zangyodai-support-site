# 残業代特化サイト - 参考資料

## SWELLテーマ設定

### SWELLスキルの使用方法

**SWELL関連の作業時は、必ず `swell` スキルを起動してください：**

```
/swell
```

スキルが起動すると、Claude Codeは以下のリソースを自動参照します：
- `.claude/resources/swell-manual/swell_manual_content.json` - 重要ページの詳細マニュアル
- `.claude/resources/swell-manual/swell_manual_links.json` - 全71ページのURL一覧

### マニュアルの読み込み方法

Claude Codeは **Pythonスクレイピング** でSWELL公式マニュアルを読み込めます：

```python
import requests
from bs4 import BeautifulSoup

url = 'https://swell-theme.com/function/88/'  # 例：メインビジュアル設定
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
article = soup.find('article')
print(article.get_text())
```

**公式マニュアル**: https://swell-theme.com/manual/

### 保存済みマニュアルデータ

以下の10ページの詳細情報が `.claude/resources/swell-manual/` に保存されています：

1. メインビジュアルの設定方法
2. ヘッダー・ロゴ画像のデザイン設定
3. フッター周りの設定方法
4. サイト全体の基本カラー設定
5. サイトのベースとなるデザイン・レイアウト設定
6. ピックアップバナー機能の使い方
7. 記事スライダーの設定方法
8. 記事一覧リストのデザイン・レイアウト設定
9. グローバルナビ（ヘッダーメニュー）の設定方法
10. スマホメニューの設定方法

---

## プロジェクト概要

- **サイト名**: 残業代サポート | 福岡発・全国対応
- **ドメイン**: zangyodai-support.com
- **プラットフォーム**: WordPress.com Business Plan
- **テーマ**: SWELL
- **メールアドレス**: info@lawyer-ak.com
- **電話番号**: 050-5482-3433

---

## 作成済みページ

1. トップページ
2. 相談の流れ
3. 費用・料金
4. 弁護士紹介
5. 事務所案内
6. よくある質問（FAQ）
7. お問い合わせ
8. プライバシーポリシー
9. 免責事項

---

## 今後のデザイン改善課題

### メインビジュアル（ヒーローエリア）のリッチ化
- **文字配置**: 左揃えに変更
- **文字サイズ**: より大きく、インパクトのあるサイズに調整
- **レイアウト**: よりリッチでプロフェッショナルなデザインに
- **参考**: SWELLマニュアルのメインビジュアル設定を確認

---

## 残タスク

- デフォルト投稿（Hello world!）の削除
- メニュー順序の調整
- 残業代計算ツールの実装
- LINE公式アカウント設定
- SEO設定
- Google Analytics設定
