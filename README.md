## AWS の設定方法

### 1.IAM ユーザーの作成

IAM は AWS リソースへのアクセスをセキュアに制御するサービス。AWS リソースを使用するユーザーやアプリケーションに対して適切なアクセス権限を付与することができる。

1.ユーザーの詳細を指定

- チェックボックス
  - 有効にすると、AWS マネジメントコンソールへのアクセスが可能なユーザーが作成できる
  - ユーザーが AWS 管理画面を操作する場合に必要である。
  - 今回は IAM ユーザーを作成して作業するためチェックを入れておく必要がある。
- ユーザタイプ : IAM ユーサーを作成します。
- コンソールパスワード : カスタムパスワード

2. 許可を設定

- 許可のオプション
  - ポリシーを直接アタッチする : 新しい IAM ユーザー専用に権限を割り当てるため。グループは今回不要。
- 必要なポリシーを検索して追加
  - AmazonSQSFullAccess : キューの作成、メッセージの送受信、削除など SQS 関連のフル権限を付与するため
  - AWSLambdaBasicExecutionRole : Lamdba 関数の基本的な実行権限を提供する。ログ出力などに必要。
  - AmazonS3ReadOnlyAccess : ファイルの読み取り専用アクセスを付与するため
