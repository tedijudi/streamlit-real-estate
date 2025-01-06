import streamlit as st
import requests
import pandas as pd
import re

# Define cookies and headers for the request
cookies = {
    'NNB': 'C6TLYOCR3UGWG',
    'ASID': '277c00ec00000182f3fe604000000049',
    'NFS': '2',
    'nid_inf': '45917648',
    'NID_AUT': 'tqKY5GkfDJD/OO2OpstZPGXgPPOFQJm03DFeLYiRy0MMVh7sFWaYXiV8U3990sog',
    'NID_JKL': 'YSelmQCO3wiWdBVKyVXzPiSuE/385Aa+uOTf/yipIB8=',
    'tooltipDisplayed': 'true',
    'recent_card_list': '1465,10340,10286,10429,2797,10395,10396',
    'NAC': '94qeC4Avim9CB',
    'ba.uuid': 'b3fc50a6-1ea0-4545-8dda-8024fabd043f',
    'NACT': '1',
    'nhn.realestate.article.rlet_type_cd': 'A01',
    'nhn.realestate.article.trade_type_cd': '""',
    'nhn.realestate.article.ipaddress_city': '4100000000',
    'REALESTATE': 'Sun Jan 05 2025 16:31:28 GMT+0900 (Korean Standard Time)',
    'BUC': 'joR6SqXFzQ6Lu5i2C5flQOPJur9Hum8ovTR3nMs-w70=',
}

headers = {
    'accept': '*/*',
    'accept-language': 'ko,en;q=0.9,en-US;q=0.8,ja;q=0.7',
    'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3MzYwNjIyODgsImV4cCI6MTczNjA3MzA4OH0.3XuHWGoTAvtyrsgPfP5vMxN9r9vmg0KuvNc9HNcabe0',
    'referer': 'https://new.land.naver.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}

# List of apartments
apartments = [
    {"id": 114098, "name": "그랑시티자이"},
    {"id": 117350, "name": "그랑시티자이2차"},
    {"id": 112013, "name": "안산파크푸르지오"},
]

# Helper function to convert deal price to numeric
def convert_price_to_numeric(price):
    if not price:
        return 0
    price = price.replace(",", "").strip()
    total_price = 0
    if "억" in price:
        parts = price.split("억")
        total_price += int(parts[0]) * 10000
        if len(parts) > 1 and parts[1]:
            total_price += int(parts[1])
    else:
        total_price += int(price)
    return total_price

# Helper function to calculate 평수
def calculate_pyeong(area):
    try:
        return round(float(area) / 3.3)  # Convert m² to 평수 and round to nearest integer
    except:
        return ""

# Streamlit App
st.title("아파트 정보 조회")
st.sidebar.header("아파트 선택")

# Sidebar selection
apartment_name = st.sidebar.selectbox(
    "관심 있는 아파트를 선택하세요", 
    [apartment["name"] for apartment in apartments]
)

# Find selected apartment ID
selected_apartment = next((apt for apt in apartments if apt["name"] == apartment_name), None)

if selected_apartment:
    st.header(f"선택된 아파트: {selected_apartment['name']}")
    st.write("선택된 아파트의 정보를 가져오는 중...")

    # Fetch data
    data_list = []
    for page in range(1, 11):  # Loop through pages 1 to 10
        url = f'https://new.land.naver.com/api/articles/complex/{selected_apartment["id"]}?realEstateType=APT%3APRE%3AABYG%3AJGC&tradeType=A1&page={page}'

        try:
            response = requests.get(url, cookies=cookies, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get("articleList", []):
                    deal_price = article.get("dealOrWarrantPrc", "")
                    deal_price_numeric = convert_price_to_numeric(deal_price)
                    area1 = article.get("area1", "")
                    area2 = article.get("area2", "")
                    data_list.append({
                        "거래금액": deal_price,
                        "층수": article.get("floorInfo", ""),
                        "공급면적": f"{area1} ({calculate_pyeong(area1)}평)",
                        "전용면적": f"{area2} ({calculate_pyeong(area2)}평)",
                        "방향": article.get("direction", ""),
                        "특징": article.get("articleFeatureDesc", ""),
                        "부동산": article.get("realtorName", ""),
                        "거래금액(숫자)": deal_price_numeric,  # For sorting
                    })
            else:
                st.error(f"Page {page}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Page {page}: {e}")

    # Sort data by numeric deal price
    if data_list:
        df = pd.DataFrame(data_list)
        df = df.sort_values(by="거래금액(숫자)", ascending=True)  # Sort by numeric price
        df = df.drop(columns=["거래금액(숫자)"])  # Remove numeric column after sorting
        st.dataframe(df[["거래금액", "층수", "공급면적", "전용면적", "방향", "특징", "부동산"]])  # Rearrange columns
    else:
        st.warning("데이터를 가져오지 못했습니다.")
