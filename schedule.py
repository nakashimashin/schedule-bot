import os
import pdfplumber
import re
from dotenv import load_dotenv

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/calendar']

load_dotenv()
CALENDAR_ID = os.getenv("CALENDAR_ID")

def readschedule(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        year = None
        month = None
        available_dates = []

        for page in pdf.pages:
            text = page.extract_text()

            # 年月の取得
            year_month_search = re.search(r"(\d{4})/(\d{1,2})/(\d{1,2})", text)
            print("正規表現: ", year_month_search)
            if year_month_search:
                year = year_month_search.group(1)
                month = year_month_search.group(2)

            # 予定の取得

            tables = page.extract_tables()

            # 複数のテーブルに対応
            for table in tables:
                date_row = None
                # 各行を取得
                for row in table:
                    if row[0] == "日":
                        date_row = row
                    # 各セルを取得
                    for i, cell in enumerate(row):
                        if cell and "コ" in cell:
                            available_dates.append({"教室番号": row[0], "日付": date_row[i]})

    return year, month, available_dates

def add_event_to_calendar(service, year, month, available_dates):
    for item in available_dates:
        date = item["日付"]
        room_num = item["教室番号"]

        event_date = f"{year}-{month.zfill(2)}-{date.zfill(2)}"
        start_time = f"{event_date}T18:00:00+09:00"
        end_time = f"{event_date}T20:30:00+09:00"

        event = {
            'summary': f'教養{room_num}',
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Tokyo',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Tokyo',
            },
            'description': '部活動',
        }

        try:
            created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

            print(f"Event created: {created_event.get('htmlLink')}")
        except HttpError as e:
            print(f"Error: {e}")

def main():
    # creds = None
    # # ユーザーのアクセスとリフレッシュトークンを格納するtoken.jsonファイルが存在する場合、token.jsonを使用して認証する。
    # if os.path.exists('token.json'):
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # # 有効な資格情報がない場合、ユーザーにログインを求める。
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    #         creds = flow.run_local_server(host="0.0.0.0", port=5001, open_browser=False)
    #     # 次回の実行のために資格情報を保存する
    #     with open('token.json', 'w') as token:
    #         token.write(creds.to_json())
    creds = service_account.Credentials.from_service_account_file(
        'service-account-key.json', scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)

    year, month, available_dates = readschedule("教室希望_教養_12月.pdf")
    print("年: ", year, "月: ", month, "利用可能日: ", available_dates)

    add_event_to_calendar(service, year, month, available_dates)

if __name__ == '__main__':
    main()