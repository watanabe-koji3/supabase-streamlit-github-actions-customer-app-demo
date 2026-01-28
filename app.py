import streamlit as st
from supabase import create_client, Client
import datetime
import os

# --- 設定と接続 ---
# Streamlit Cloud上では st.secrets、ローカルでは .streamlit/secrets.toml から読み込む
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("顧客管理システム")

# --- タブで機能を分ける ---
tab1, tab2 = st.tabs(["📝 顧客登録", "🔍 顧客表示"])

# --- タブ1: 顧客登録 ---
with tab1:
    st.header("新規登録")
    
    with st.form("register_form"):
        name = st.text_input("顧客名")
        date = st.date_input("関与日", value=datetime.date.today())
        desc = st.text_area("事業内容 (空欄可)")
        
        submitted = st.form_submit_button("顧客登録ボタン")
        
        if submitted:
            if not name:
                st.error("顧客名は必須です。")
            else:
                # Supabaseへのデータ送信 (UUIDと作成日時はDB側で自動生成)
                data = {
                    "customer_name": name,
                    "engagement_date": str(date),
                    "business_desc": desc
                }
                
                try:
                    response = supabase.table("customers").insert(data).execute()
                    
                    # 登録されたデータのUUIDを取得
                    new_uuid = response.data[0]['call_id']
                    
                    st.success("登録完了！")
                    st.write("以下の呼び出しIDを控えてください（コピーボタン推奨）")
                    
                    # コピーしやすいようにコードブロックで表示
                    st.code(new_uuid, language="text")
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

# --- タブ2: 顧客表示 ---
with tab2:
    st.header("情報照会")
    
    search_uuid = st.text_input("呼び出しID (UUID) を入力")
    search_btn = st.button("顧客表示")
    
    if search_btn and search_uuid:
        try:
            # Supabaseから検索
            response = supabase.table("customers").select("*").eq("call_id", search_uuid).execute()
            
            if response.data:
                record = response.data[0]
                
                # --- 日時変換処理 (UTC -> JST) ---
                # DBから取得したUTC日時文字列をdatetimeオブジェクトへ
                dt_utc = datetime.datetime.fromisoformat(record['created_at'])
                # 9時間足してJSTへ変換
                dt_jst = dt_utc.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
                # 読みやすい形式に整形 (例: 2026年01月28日 10時23分)
                formatted_date = dt_jst.strftime('%Y年%m月%d日 %H時%M分')
                
                st.markdown("### 顧客情報")
                st.write(f"**顧客名:** {record['customer_name']}")
                st.write(f"**関与日:** {record['engagement_date']}")
                st.write(f"**事業内容:** {record['business_desc']}")
                st.write(f"**作成日時:** {formatted_date}")
            else:
                st.warning("該当する顧客情報が見つかりませんでした。")
                
        except Exception as e:
            st.error(f"検索エラー: {e}")