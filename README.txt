============================================================
  Mewgenics 日本語MOD
============================================================

■ インストール方法

  【重要】 まず Steam でファイルの整合性を確認してください。
    Steam → Mewgenics → 右クリック → プロパティ
    → インストール済みファイル → ファイルの整合性を確認

  1. このフォルダ内の install.bat をダブルクリック
  2. ゲームを起動すると自動で日本語化されます

  ※ 管理者権限は不要です
  ※ Pythonのインストールは不要です
  ※ 初回起動時は gpak (約5GB) の再構築が走ります。
     進捗ウィンドウが表示されるので、完了までお待ちください。


■ アンインストール方法

  uninstall.bat をダブルクリック
  MODファイルの削除とゲームデータの復元が行われます。

  より確実にしたい場合は、アンインストール後に
  Steam でファイルの整合性を確認してください。


■ 動作要件

  - Windows 10/11 (64bit)
  - Steam版 Mewgenics


■ ゲームアップデート後

  ゲームがアップデートされると、DLLが自動的にgpakを
  再構築します。翻訳データが古い場合はダイアログで
  通知されるので、最新版をダウンロードしてください。

  1. Steam でファイルの整合性を確認
  2. 最新版の MOD をダウンロード
     https://github.com/ibushimaru/MewgenicsJP/releases
  3. install.bat を再度実行


■ トラブルシューティング

  Q: メニュー画面等のテキストが一切表示されない

  A: MOD が無効な状態で言語設定が ja のままになっている
     場合に発生します。以下の方法で復旧できます。

     方法1: Steam でファイルの整合性を確認した後、
            install.bat を再実行

     方法2: 言語設定ファイルを手動で修正する
       1. Win+R →「%appdata%\Glaiel Games\Mewgenics」を開く
       2. 数字フォルダ(Steam ID)の中の settings.txt を開く
       3.「current_language ja」を
         「current_language en」に書き換えて保存

  Q: install.bat が一瞬で閉じる
  A: install.bat を右クリック →「管理者として実行」を
     試してください。

  Q: ゲームフォルダが見つからないと表示される
  A: 手動でゲームフォルダのパスを入力してください。
     例: D:\SteamLibrary\steamapps\common\Mewgenics

  Q: ログを確認したい
  A: ゲームフォルダ内の MewgenicsJP\mewgenics_jp.log に
     DLLの動作ログが記録されています。


■ 不具合報告・連絡先

  MODの不具合やテキストが表示されない等の
  トラブルがあれば、以下にご連絡ください。

  X (Twitter): @ibushi_maru
  Discord: 燻丸
  GitHub: https://github.com/ibushimaru/MewgenicsJP/issues


■ クレジット

  翻訳: ibushimaru
  フォント: Yusei Magic (SIL Open Font License)
  https://github.com/tanukifont/YuseiMagic

============================================================
