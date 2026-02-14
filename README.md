# Mewgenics 日本語MOD

Edmund McMillen制作「Mewgenics」の日本語翻訳MODです。

## インストール方法

1. [Releases](../../releases) から最新の `MewgenicsJP-vX.X.X.zip` をダウンロード
2. 任意の場所に展開
3. `install.bat` をダブルクリック

ゲームフォルダの検出から言語設定の切り替えまで、すべて自動で行われます。

## アンインストール

`uninstall.bat` をダブルクリックしてください。
ゲームファイルと言語設定が自動で元に戻ります。

## 動作要件

- Windows 10/11 (64bit)
- Steam版 Mewgenics
- Python不要 (同梱済み)

## ゲームアップデート後

Steamのアップデートでゲームファイルが上書きされると、MODが無効になりゲームが起動できなくなる場合があります。
`install.bat` を再度実行してください。MODが再適用されます。

**推奨**: Steamの自動アップデートを制限しておくと安全です。
Steam → Mewgenics → プロパティ → アップデート → 「起動時にのみアップデート」に変更

## トラブルシューティング

### 「UNSUPPORTED LANGUAGE」と表示されてゲームが起動できない

Steamのアップデートで MOD が上書きされた場合に発生します。
以下のいずれかの方法で復旧できます。

**方法1**: `install.bat` を再度実行する

**方法2**: 言語設定ファイルを手動で修正する

1. `Win+R` → `%appdata%\Glaiel Games\Mewgenics` を開く
2. 数字のフォルダ (Steam ID) の中にある `settings.txt` を開く
3. `current_language ja` を `current_language en` に書き換えて保存

## 不具合報告・連絡先

MODの不具合やゲームが起動できない等のトラブルがあれば、以下にご連絡ください。

- X (Twitter): [@ibushi_maru](https://x.com/ibushi_maru)
- Discord: 燻丸
- GitHub: [Issues](../../issues)

## 技術情報

- フォント: Yusei Magic
- ワードラップ: BudouX + ZWSP (Zero Width Space) による自然な改行
- パッチ方式: gpak デルタリパック + exe バイナリパッチ

## ライセンス

翻訳テキストおよびツールのライセンスについては [LICENSE](LICENSE) を参照してください。

## クレジット

- 翻訳: ibushimaru
- フォント: [Yusei Magic](https://github.com/tanukifont/YuseiMagic) (SIL Open Font License)
- ワードラップ: [BudouX](https://github.com/google/budoux) ベースの改行処理
