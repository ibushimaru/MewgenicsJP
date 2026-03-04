# Mewgenics 日本語MOD

Edmund McMillen制作「Mewgenics」の日本語翻訳MODです。

## インストール方法

1. [Releases](../../releases) から最新の `MewgenicsJP-vX.X.X.zip` をダウンロード
2. 任意の場所に展開
3. `install.bat` をダブルクリック

ゲームフォルダの検出から言語設定の切り替えまで、すべて自動で行われます。

## アンインストール

`uninstall.bat` をダブルクリックしてください。
以下の2つのモードを選択できます。

1. **言語設定のみリセット** — ゲーム更新後にテキストが表示されなくなった場合の復旧用
2. **完全アンインストール** — ゲームファイルと言語設定を元に戻す

## 動作要件

- Windows 10/11 (64bit)
- Steam版 Mewgenics
- Python不要 (同梱済み)

## ゲームアップデート後

Steamのアップデートにより MOD が無効になり、メニュー画面等のテキストが一切表示されなくなる場合があります。

1. `uninstall.bat` を実行 →「言語設定のみリセット」を選択
2. [Releases](../../releases) ページから最新版の MOD をダウンロード
3. `install.bat` を実行

ゲームのアップデートにより exe の内部構造が変更された場合、
最新版の MOD でも対応できないことがあります。
その場合は下記の連絡先までお問い合わせください。

## トラブルシューティング

### メニュー画面等のテキストが一切表示されない

MOD が無効な状態で言語設定が ja のままになっている場合に発生します。
以下のいずれかの方法で復旧できます。

**方法1**: `uninstall.bat` を実行 →「言語設定のみリセット」を選択

**方法2**: 言語設定ファイルを手動で修正する

1. `Win+R` → `%appdata%\Glaiel Games\Mewgenics` を開く
2. 数字のフォルダ (Steam ID) の中にある `settings.txt` を開く
3. `current_language ja` を `current_language en` に書き換えて保存

## 不具合報告・連絡先

MODの不具合やテキストが表示されない等のトラブルがあれば、以下にご連絡ください。

- X (Twitter): [@ibushi_maru](https://x.com/ibushi_maru)
- Discord: 燻丸
- GitHub: [Issues](../../issues)

## クレジット

- 翻訳: ibushimaru
- フォント: [Yusei Magic](https://github.com/tanukifont/YuseiMagic) (SIL Open Font License)
- ワードラップ: [BudouX](https://github.com/google/budoux) ベースの改行処理
