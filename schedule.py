import datetime
import os.path
import pdfplumber
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']


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


def main():
    creds = None
    # ユーザーのアクセスとリフレッシュトークンを格納するtoken.jsonファイルが存在する場合、token.jsonを使用して認証する。
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 有効な資格情報がない場合、ユーザーにログインを求める。
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 次回の実行のために資格情報を保存する
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


    year, month, available_dates = readschedule("教室希望_教養_12月.pdf")
    print("年: ", year, "月: ", month, "利用可能日: ", available_dates)


    service = build('calendar', 'v3', credentials=creds)


if __name__ == '__main__':
    main()