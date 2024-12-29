import json

def lambda_handler(event, context):
    # SQSメッセージを処理
    print("=== イベント受信 ===")
    print(json.dumps(event))  # 受信したイベントをログに出力

    # メッセージ処理
    for record in event['Records']:
        body = record['body']  # メッセージ本文
        print(f"受信メッセージ: {body}")

    # 成功レスポンスを返す
    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully!')
    }
