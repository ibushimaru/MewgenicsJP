# Mewgenics 日本語MOD

Edmund McMillen制作「Mewgenics」の日本語翻訳MODです。

## インストール方法

1. **Steam でファイルの整合性を確認してください**
   - Steam → Mewgenics → 右クリック → プロパティ → インストール済みファイル → ファイルの整合性を確認
2. [Releases](../../releases) から最新の `MewgenicsJP-vX.X.X.zip` をダウンロード
3. 任意の場所に展開
4. `install.bat` をダブルクリック
5. ゲームを起動すると自動で日本語化されます

初回起動時は約 5GB の `resources.gpak` の再構築が走ります。進捗ウィンドウ (`MewgenicsJP_progress.exe`) が表示されるので、完了までお待ちください。

## 仕組み

ゲーム起動時に `version.dll` が自動で翻訳テキストとフォントを適用します。Exe の書き換えは行わず、メモリ上で改行処理のパッチを当てるだけです。

gpak 再構築中は別プロセスの進捗ウィンドウ (`MewgenicsJP_progress.exe`) が状況を表示します。

## アンインストール

`uninstall.bat` をダブルクリックしてください。
MODファイルの削除とゲームデータの復元が行われます。

より確実にしたい場合は、アンインストール後に Steam でファイルの整合性を確認してください。

## v1.x からの移行

旧バージョン (v1.0.x) をお使いの方は、先に旧版の `uninstall.bat` を実行するか、
Steam でファイルの整合性を確認してからインストールしてください。

## 動作要件

- Windows 10/11 (64bit)
- Steam版 Mewgenics

## ゲームアップデート後

ゲームがアップデートされると、DLLが自動的にgpakを再構築します。

### 翻訳が追従していない箇所は英語で表示されます

ゲーム本体のテキストが変更されているのに翻訳データが古い場合、その「変更された行だけ」が英語の原文で表示されます。日本語訳が古くて意味が変わっている、という事故を防ぐためです。

例: バランス調整で「Blizzard(ブリザード)」の説明が変わると、その行のみ英語表示に切り替わります。他の翻訳済みの行は通常通り日本語で表示されます。

英語表示になっている行が 1 行でもある場合、ゲーム起動時に以下のようなダイアログが表示されます:

```
ゲーム本体のテキスト変更に翻訳が追いついていません。
N 行のテキストが英語で表示されます。
```

`N` が英語表示に切り替わっている行数です。最新版のMODに更新すると `N=0` になり、ダイアログも出なくなります。

### 翻訳を最新化したい場合

1. Steam でファイルの整合性を確認
2. [Releases](../../releases) ページから最新版をダウンロード
3. `install.bat` を再度実行

## トラブルシューティング

### メニュー画面等のテキストが一切表示されない

MOD が無効な状態で言語設定が ja のままになっている場合に発生します。

**方法1**: Steam でファイルの整合性を確認した後、`install.bat` を再実行

**方法2**: 言語設定ファイルを手動で修正する

1. `Win+R` → `%appdata%\Glaiel Games\Mewgenics` を開く
2. 数字のフォルダ (Steam ID) の中にある `settings.txt` を開く
3. `current_language ja` を `current_language en` に書き換えて保存

### ログの確認

問題が発生した場合、ゲームフォルダ内の `MewgenicsJP/mewgenics_jp.log` にDLLの動作ログが記録されています。

## 不具合報告・連絡先

MODの不具合やテキストが表示されない等のトラブルがあれば、以下にご連絡ください。

- X (Twitter): [@ibushi_maru](https://x.com/ibushi_maru)
- Discord: 燻丸
- GitHub: [Issues](../../issues)

## クレジット

- 翻訳: ibushimaru
- フォント: [Yusei Magic](https://github.com/tanukifont/YuseiMagic) (SIL Open Font License)
- ワードラップ: [BudouX](https://github.com/google/budoux) ベースの改行処理
