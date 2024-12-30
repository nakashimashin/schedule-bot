import os
import json
import requests
import pdfplumber
import re
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

# 環境変数から設定を読み込み
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CALENDAR_ID = os.getenv("CALENDAR_ID")

SCOPES = ['https://www.googleapis.com/auth/calendar']

def lambda_handler(event, context):
    """
    SQSからイベントを受け取り、Slack API経由でPDFを取得し、Googleカレンダーに登録する
    """
    print("=== イベント受信 ===")
    print(json.dumps(event))  # 受信したイベントをログに出力

    for record in event['Records']:
        # SQSメッセージの解析
        body = json.loads(record['body'])
        print(f"受信メッセージ: {body}")

        # Slack APIからファイルURLを取得
        file_id = body['event']['file']['id']
        file_url = get_file_url(file_id)
        print(f"取得したPDFファイルのURL: {file_url}")

        # PDF処理を実行
        download_and_process_pdf(file_url)

    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully!')
    }

def get_file_url(file_id):
    """
    Slack APIからファイル情報を取得し、ファイルURLを返す
    """
    headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
    file_info_url = f'https://slack.com/api/files.info?file={file_id}'
    response = requests.get(file_info_url, headers=headers)
    file_info = response.json()
    print(f"Slack API ファイル情報の応答: {file_info}")

    return file_info.get('file', {}).get('url_private')

def download_and_process_pdf(file_url, file_name='/tmp/temp.pdf'):
    """
    PDFをダウンロードし、Googleカレンダーに予定を追加する
    """
    headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
    response = requests.get(file_url, headers=headers, stream=True)

    with open(file_name, 'wb') as pdf_file:
        for chunk in response.iter_content(chunk_size=8192):
            pdf_file.write(chunk)

    # PDFからスケジュールを取得
    year, month, available_dates = readschedule(file_name)

    # Googleカレンダーに登録
    creds = service_account.Credentials.from_service_account_file(
        '/var/task/service-account-key.json', scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=creds)
    add_event_to_calendar(service, year, month, available_dates)

def readschedule(pdf_path):
    """
    PDFを解析してスケジュールを抽出する
    """
    with pdfplumber.open(pdf_path) as pdf:
        year = None
        month = None
        available_dates = []

        for page in pdf.pages:
            text = page.extract_text()

            # 年月の取得
            year_month_search = re.search(r"(\d{4})/(\d{1,2})/(\d{1,2})", text)
            if year_month_search:
                year = year_month_search.group(1)
                month = year_month_search.group(2)

            # 予定の取得
            tables = page.extract_tables()
            for table in tables:
                date_row = next((row for row in table if row[0] == "日"), None)
                if not date_row:
                    continue

                for row in table:
                    if row[0] == "日":
                        continue
                    for i, cell in enumerate(row):
                        if "コ" in str(cell):
                            available_dates.append({"教室番号": row[0], "日付": date_row[i]})

    return year, month, available_dates

def add_event_to_calendar(service, year, month, available_dates):
    """
    Googleカレンダーに予定を追加する
    """
    for item in available_dates:
        date = item["日付"]
        room_num = item["教室番号"]

        event_date = f"{year}-{month.zfill(2)}-{date.zfill(2)}"
        start_time = f"{event_date}T18:00:00+09:00"
        end_time = f"{event_date}T20:30:00+09:00"

        event = {
            'summary': f'教養{room_num}',
            'start': {'dateTime': start_time, 'timeZone': 'Asia/Tokyo'},
            'end': {'dateTime': end_time, 'timeZone': 'Asia/Tokyo'},
            'description': '部活動',
        }

        try:
            created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
            print(f"Event created: {created_event.get('htmlLink')}")
        except HttpError as e:
            print(f"Error: {e}")
