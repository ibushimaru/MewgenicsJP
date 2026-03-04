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
  以下の2つのモードを選択できます。

  1. 言語設定のみリセット
     ゲーム更新後にテキストが表示されなくなった場合の復旧用

  2. 完全アンインストール
     ゲームファイルと言語設定を元に戻す


■ 動作要件

  - Windows 10/11 (64bit)
  - Steam版 Mewgenics


■ ゲームアップデート後

  Steamのアップデートにより MOD が無効になり、
  メニュー画面等のテキストが一切表示されなくなる場合があります。

  1. uninstall.bat を実行 →「言語設定のみリセット」を選択
  2. 最新版の MOD をダウンロード
     https://github.com/ibushimaru/MewgenicsJP/releases
  3. install.bat を再度実行

  ゲームのアップデートにより exe の内部構造が変更された場合、
  最新版の MOD でも対応できないことがあります。
  その場合は下記の連絡先までお問い合わせください。


■ トラブルシューティング

  Q: メニュー画面等のテキストが一切表示されない

  A: MOD が無効な状態で言語設定が ja のままになっている
     場合に発生します。以下のいずれかの方法で復旧できます。

     方法1: uninstall.bat を実行
            →「言語設定のみリセット」を選択

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
