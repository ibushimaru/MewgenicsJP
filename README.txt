============================================================
  Mewgenics 日本語MOD
============================================================

■ インストール方法

  1. このフォルダ内の install.bat をダブルクリック
  2. すべて自動で完了します
  3. ゲームを起動すると日本語で表示されます

  ※ 管理者権限は不要です
  ※ Pythonのインストールは不要です (同梱済み)


■ アンインストール方法

  uninstall.bat をダブルクリック
  ゲームファイルと言語設定が自動で元に戻ります。


■ ゲームアップデート後  *** 重要 ***

  Steamのアップデートでゲームファイルが上書きされると、
  MODが無効になりゲームが起動できなくなる場合があります。

  → install.bat を再度実行してください。

  ※ ゲームのアップデートにより exe の内部構造が変更された
     場合、ワードラップパッチが適用できなくなることがあります。
     その場合は MOD の新バージョンで対応しますので、
     GitHub の Releases ページで最新版を確認するか、
     下記の連絡先までお問い合わせください。


■ トラブルシューティング

  Q: 「UNSUPPORTED LANGUAGE」と表示されて起動できない

  A: Steamのアップデートで MOD が上書きされた場合に発生します。
     以下のいずれかの方法で復旧できます。

     方法1: install.bat を再度実行する

     方法2: 言語設定ファイルを手動で修正する
       1. Win+R →「%appdata%\Glaiel Games\Mewgenics」を開く
       2. 数字フォルダ(Steam ID)の中の settings.txt を開く
       3. 「current_language ja」を
          「current_language en」に書き換えて保存

  Q: install.bat が一瞬で閉じる
  A: install.bat を右クリック →「管理者として実行」を
     試してください。

  Q: ゲームフォルダが見つからないと表示される
  A: 手動でゲームフォルダのパスを入力してください。
     例: D:\SteamLibrary\steamapps\common\Mewgenics

  Q: ワードラップがおかしい (テキストが1行に詰まる)
  A: install.bat を再度実行してください。


■ 不具合報告・連絡先

  MODの不具合やゲームが起動できない等の
  トラブルがあれば、以下にご連絡ください。

  X (Twitter): @ibushi_maru
  Discord: 燻丸
  GitHub: https://github.com/ibushimaru/MewgenicsJP/issues


■ 技術情報

  - フォント: Yusei Magic
  - ワードラップ: BudouX + ZWSP による自然な改行
  - パッチ方式: gpak デルタリパック + exe バイナリパッチ


■ クレジット

  翻訳: ibushimaru
  フォント: Yusei Magic (SIL Open Font License)
  https://github.com/tanukifont/YuseiMagic

============================================================
