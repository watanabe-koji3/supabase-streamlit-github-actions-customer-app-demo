import os
import datetime
from supabase import create_client, Client

# GitHub ActionsのSecretsから環境変数を読み込む
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("環境変数 SUPABASE_URL または SUPABASE_KEY が設定されていません")

supabase: Client = create_client(url, key)

def delete_old_records():
    # 現在時刻から24時間前を計算 (UTC)
    time_threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
    threshold_str = time_threshold.isoformat()
    
    print(f"{threshold_str} 以前のデータを削除します...")

    try:
        # created_at が 24時間前より小さい(lt: less than)データを削除
        response = supabase.table("customers").delete().lt("created_at", threshold_str).execute()
        
        # response.data は削除された行のリスト
        deleted_count = len(response.data)
        print(f"削除完了: {deleted_count} 件のデータを削除しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    delete_old_records()