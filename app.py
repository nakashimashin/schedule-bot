import os
import requests
from flask import Flask, request, jsonify
from schedule import readschedule, add_event_to_calendar
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CALENDAR_ID = os.getenv("CALENDAR_ID")

app = Flask(__name__)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    print("=== リクエスト受信 ===")
    print(f"Headers: {request.headers}")
    print(f"Data: {request.data}")

    # ボディの解析と内容の確認
    body = request.get_json(force=True)
    print(f"Request Body: {body}")

    # Challenge確認
    if 'challenge' in body:
        print("Challenge received. Responding with challenge.")
        return body['challenge']

    # イベントIDとタイムスタンプのログ
    event_id = body.get('event_id')
    event_time = body.get('event_time')
    print(f"イベントID: {event_id}, タイムスタンプ: {event_time}")

    # イベントタイプの確認
    event_type = body.get('event', {}).get('type')
    print(f"イベントタイプ: {event_type}")

    # ファイル共有イベントの処理確認
    if 'event' in body and event_type == 'file_shared':
        print("ファイル共有イベントを受信しました。")

        # ファイルIDの取得とログ出力
        file_id = body['event']['file']['id']
        print(f"ファイルID: {file_id}")

        # Slack APIでファイル情報の取得
        headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
        file_info_url = f'https://slack.com/api/files.info?file={file_id}'
        response = requests.get(file_info_url, headers=headers)
        file_info = response.json()
        print(f"Slack API ファイル情報の応答: {file_info}")

        # ファイルURLの取得
        file_url = file_info.get('file', {}).get('url_private')
        print(f"取得したPDFファイルのURL: {file_url}")

        # ファイル処理の開始ログ
        print("PDFファイルの処理を開始します。")
        download_and_process_pdf(file_url)
        print("PDFファイルの処理が完了しました。")

        return jsonify({'status': 'File processing successfully'})

    # 未処理のイベント
    print("未処理のイベントを受信しました。")
    return jsonify({'status': 'Event not handled'})

def download_and_process_pdf(file_url, file_name='temp.pdf'):
    print("発火しました")
    headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
    response = requests.get(file_url, headers=headers, stream=True)

    with open(file_name, 'wb') as pdf_file:
        for chunk in response.iter_content(chunk_size=8192):
            pdf_file.write(chunk)

    # PDFからスケジュールを取得
    year, month, available_dates = readschedule(file_name)

    # Googleカレンダーに登録
    creds = service_account.Credentials.from_service_account_file(
        'service-account-key.json', scopes=['https://www.googleapis.com/auth/calendar']
    )

    service = build('calendar', 'v3', credentials=creds)
    add_event_to_calendar(service, year, month, available_dates)


if __name__ == '__main__':
    print("Starting Flask app!!")
    app.run(host="0.0.0.0", port=5001, debug=True)

