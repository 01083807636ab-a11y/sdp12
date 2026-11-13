"""냉장뾱 | 실행: streamlit run app.py
SQLite 로컬 저장. Streamlit Community Cloud 로컬 디스크는 영구 저장소가 아닙니다.
"""
import json
import os
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="냉장뾱", page_icon="🧊", layout="wide")


def brand_logo():
    # A single shared lockup prevents splash and home logos from drifting apart.
    return '<div class="nb-logo" role="img" aria-label="냉장뾱 로고"><span class="nb-mark" aria-hidden="true"><i></i><b></b></span><span class="nb-type"><span class="nb-name">FRIDGE<span class="nb-dot">.</span>POP</span><span class="nb-sub">FRESH LIVING, TOGETHER</span></span></div>'

st.html("""<style>
.nb-logo {display:flex;align-items:center;justify-content:center;gap:15px;
  font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic",sans-serif;}
.nb-mark {display:block;position:relative;width:58px;height:66px;flex:none;
  border-radius:19px;background:#153e35;box-shadow:0 6px 16px #153e3518;}
.nb-mark:before {content:'';position:absolute;left:14px;right:14px;top:26px;height:2px;background:#c8ad75;border-radius:2px;}
.nb-mark i,.nb-mark b {position:absolute;left:15px;width:3px;border-radius:3px;background:#effbf5;}
.nb-mark i {top:14px;height:7px;}.nb-mark b {top:34px;height:15px;}
.nb-mark:after {content:'';position:absolute;right:10px;top:10px;width:6px;height:6px;border-radius:50%;background:#c8ad75;}
.nb-type {display:flex;flex-direction:column;gap:7px;}
.nb-name {font-family:"Avenir Next","Helvetica Neue",Arial,sans-serif;font-size:30px;font-weight:600;letter-spacing:2px;line-height:1.2;color:#153e35;white-space:nowrap;}
.nb-sub {font-family:Arial,sans-serif;font-size:8px;letter-spacing:2.2px;color:#75684e;font-weight:600;}
@media(max-width:380px){.nb-logo{gap:11px}.nb-name{font-size:24px;letter-spacing:1.5px}.nb-sub{font-size:7px;letter-spacing:1.5px}.nb-mark{width:50px;height:60px}}
.nb-dot {color:#b08d50;}
.nb-home {margin:8px 0 22px;}.nb-home .nb-logo {justify-content:flex-start;}
.bbyok-intro {position:fixed;inset:0;z-index:999990;background:#f7f5ef;display:flex;
  align-items:center;justify-content:center;pointer-events:none;animation:nb-away .35s 1.7s forwards;}
.nb-splash {animation:nb-pop .7s cubic-bezier(.2,.9,.3,1.2) both;}
@keyframes nb-pop {0%{opacity:0;transform:translateY(18px) scale(.65)}65%{opacity:1;transform:scale(1.06)}100%{opacity:1;transform:scale(1)}}
@keyframes nb-away {to{opacity:0;visibility:hidden;}}
@media(prefers-reduced-motion:reduce){.nb-splash{animation:none}.bbyok-intro{animation:nb-away .01s .6s forwards}}
</style>""")

def show_brand_intro():
    if st.session_state.get("naengjang_bbyok_intro_seen"):
        return
    st.session_state["naengjang_bbyok_intro_seen"] = True
    st.html('<div class="bbyok-intro" role="status" aria-label="냉장뾱 시작 화면"><div class="nb-splash">'+brand_logo()+'</div></div>')

show_brand_intro()


def apply_mobile_theme():
    st.html("""
    <style>
    :root {color-scheme:light; --mint:#17785f; --ink:#164c3f; --lemon:#ffdf79;}
    *, *::before, *::after {box-sizing:border-box;}
    [data-testid="stAppViewContainer"] {
      background-color:#eaf8f0;
      background-image:radial-gradient(ellipse at 0% 12%,#b3ebd5 0%,transparent 38%),
        radial-gradient(ellipse at 100% 40%,#ffedac 0%,transparent 40%),
        radial-gradient(ellipse at 25% 90%,#c8eee5 0%,transparent 35%),
        radial-gradient(#85bda54d 1.4px,transparent 1.4px);
      background-size:auto,auto,auto,24px 24px;
      color:var(--ink);
    }
    [data-testid="stHeader"] {background:#eaf8f0ed;}
    [data-testid="stMainBlockContainer"] {
      max-width:940px; padding:2.8rem 1.5rem 4rem;
    }
    [data-testid="stMain"] {overflow-x:hidden;}
    h1,h2,h3,p,label,[data-testid="stCaptionContainer"] {color:var(--ink)!important;}
    h1 {font-weight:900!important;letter-spacing:-1.4px;}
    [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"]>div {
      background:#ffffffed;border-radius:22px!important;
      border-color:#c9e8d9!important;
    }
    [data-testid="stForm"] {padding:20px!important;box-shadow:0 6px 20px #17553d09;}
    [data-testid="stExpander"] {
      background:#ffffffec;border-radius:18px; border:1px solid #c9e8d9;
    }
    [data-testid="stExpander"] details {border:none!important;}
    [data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button,
    [data-testid="stDownloadButton"] button,[data-testid="stPopover"] button {
      min-height:48px;border-radius:14px;border:1px solid #b8d9c9;
      font-weight:700;background:#fff;color:var(--ink);
    }
    button[kind="primary"] {background:#17785f!important;color:#fff!important;border-color:#17785f!important;}
    button[kind="primary"] p {color:#fff!important;}
    /* Explicit foreground AND background keep fields readable in dark-mode browsers. */
    input,textarea,input:disabled,textarea:disabled {
      font-size:16px!important;line-height:1.5!important;
      color:#173c32!important;-webkit-text-fill-color:#173c32!important;
      caret-color:#12664d!important;background:#ffffff!important;opacity:1!important;
    }
    input::placeholder,textarea::placeholder {
      color:#52685f!important;-webkit-text-fill-color:#52685f!important;opacity:1!important;
    }
    [data-baseweb="input"],[data-baseweb="base-input"],
    [data-baseweb="textarea"],[data-baseweb="select"]>div {
      background:#ffffff!important;color:#173c32!important;border-radius:12px!important;
    }
    [data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div {
      border:2px solid #688f7d!important;box-shadow:0 2px 5px #164c3f0d!important;
      min-height:50px;
    }
    [data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,
    [data-baseweb="select"]:focus-within>div {
      border-color:#12664d!important;box-shadow:0 0 0 3px #17785f26!important;
    }
    [data-baseweb="select"] span,[data-baseweb="select"] div {
      color:#173c32!important;-webkit-text-fill-color:#173c32!important;
    }
    [data-baseweb="input"] button,[data-baseweb="input"] svg,
    [data-baseweb="select"] svg {color:#173c32!important;fill:currentColor!important;}
    [data-baseweb="input"] button {background:#eef7f1!important;}
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="popover"] [role="option"] {
      background:#fff!important;color:#173c32!important;
    }
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [aria-selected="true"] {background:#d9f2e5!important;}
    [data-testid="stWidgetLabel"] p {font-weight:700!important;color:#173c32!important;}
    [data-testid="stAlert"] {border-radius:16px;}
    .bbyok-hero {position:relative;overflow:hidden; padding:25px 26px;margin:0 0 12px;
      border-radius:26px;background:linear-gradient(115deg,#176c55,#278a6a);
      color:#fff;box-shadow:0 12px 28px #17553d18;}
    .bbyok-hero:after {content:'';position:absolute;width:190px;height:190px;
      right:-55px;top:-75px;border:28px solid #ffffff18;border-radius:50%;pointer-events:none;}
    .bbyok-hero .eyebrow {font-size:12px;font-weight:800;letter-spacing:2px;color:#c9f4df;}
    .bbyok-hero .headline {font-size:29px;font-weight:900;line-height:1.4;margin:8px 0;letter-spacing:-1px;}
    .bbyok-hero .sub {font-size:14px;line-height:1.7;color:#e1f7ec;}
    .bbyok-produce {margin-top:19px;display:flex;flex-wrap:wrap;gap:9px;}
    .bbyok-produce span {background:#ffffff18;border:1px solid #ffffff29;border-radius:15px;
      padding:8px 12px;font-size:24px; transform:rotate(-5deg);}
    .bbyok-produce span:nth-child(even) {transform:rotate(5deg);background:#ffdf79;}
    @media(max-width:640px) {
      [data-testid="stMainBlockContainer"] {padding:1.3rem .85rem max(2rem,env(safe-area-inset-bottom));}
      h1 {font-size:2rem!important;} h2,h3 {font-size:1.25rem!important;}
      [data-testid="stHorizontalBlock"] {flex-wrap:wrap!important;gap:.75rem!important;}
      [data-testid="stColumn"] {width:100%!important;flex:1 1 100%!important;min-width:0!important;}
      [data-testid="stForm"] {padding:14px!important;}
      .bbyok-hero {padding:22px 19px;border-radius:22px;}
      .bbyok-hero .headline {font-size:25px;}
      .bbyok-produce {gap:7px;} .bbyok-produce span {font-size:22px;padding:7px 10px;}
      [data-testid="stPopoverBody"] {max-width:calc(100vw - 24px)!important;}
    }
    </style>
    """)

apply_mobile_theme()

DB_PATH = Path(os.environ.get("FRIDGE_DB_PATH", "fridge_data.sqlite3"))
UNITS = ["개", "g", "kg", "ml", "L", "봉", "팩", "병"]
LOCATIONS = ["냉장", "냉동", "실온"]
SOURCES = ["식재료 직접 등록", "영수증 보고 입력"]


def connect():
    conn = sqlite3.connect(str(DB_PATH), timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def initialize():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
        CREATE TABLE IF NOT EXISTS receipt_categories(
            id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
        CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, category TEXT NOT NULL,
            source TEXT NOT NULL, receipt_category TEXT NOT NULL DEFAULT '',
            receipt_ref TEXT NOT NULL DEFAULT '', quantity REAL NOT NULL CHECK(quantity >= 0),
            unit TEXT NOT NULL, location TEXT NOT NULL,
            purchase_date TEXT NOT NULL, expiry_date TEXT NOT NULL,
            memo TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL REFERENCES items(id),
            item_name TEXT NOT NULL, action TEXT NOT NULL,
            quantity REAL NOT NULL CHECK(quantity > 0), unit TEXT NOT NULL,
            reason TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL);
        """)
        for n in ["채소", "과일", "육류", "수산물", "유제품·달걀", "반찬·가공식품", "양념", "기타"]:
            c.execute("INSERT OR IGNORE INTO categories(name) VALUES(?)", (n,))
        for n in ["마트", "온라인 장보기", "시장", "편의점", "기타"]:
            c.execute("INSERT OR IGNORE INTO receipt_categories(name) VALUES(?)", (n,))


def records(table):
    # Table names are internal constants, never user input.
    if table not in {"items", "logs", "categories", "receipt_categories"}:
        raise ValueError("허용되지 않은 테이블")
    with connect() as c:
        return [dict(r) for r in c.execute(f"SELECT * FROM {table} ORDER BY id")]


def names(table):
    return [r["name"] for r in records(table)]


def valid_text(value, label):
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "nat"}:
        raise ValueError(f"{label}을(를) 입력해 주세요.")
    if len(text) > 500:
        raise ValueError(f"{label}은(는) 500자 이내로 입력해 주세요.")
    return text


def normalize(row):
    q = float(row["수량"])
    if not 0 < q <= 1_000_000:
        raise ValueError("수량은 0 초과 1,000,000 이하여야 합니다.")
    bought = pd.to_datetime(row["구매일"], errors="raise").date()
    expiry = pd.to_datetime(row["기한"], errors="raise").date()
    if pd.isna(bought) or pd.isna(expiry):
        raise ValueError("구매일과 기한을 입력해 주세요.")
    if expiry < bought:
        raise ValueError("기한은 구매일보다 빠를 수 없습니다.")
    cat = valid_text(row["식재료 분류"], "식재료 분류")
    src = valid_text(row["입력 방식"], "입력 방식")
    unit = valid_text(row["단위"], "단위")
    loc = valid_text(row["보관 장소"], "보관 장소")
    rc = str(row.get("영수증 분류", "") or "").strip()
    if cat not in names("categories") or src not in SOURCES or unit not in UNITS or loc not in LOCATIONS:
        raise ValueError("분류·입력 방식·단위·보관 장소를 선택지에서 골라 주세요.")
    if src == SOURCES[1] and rc not in names("receipt_categories"):
        raise ValueError("영수증 분류를 선택해 주세요.")
    return (valid_text(row["상품명"], "상품명"), cat, src, rc,
            str(row.get("영수증 메모", "") or ""), q, unit, loc,
            bought.isoformat(), expiry.isoformat(), str(row.get("메모", "") or ""))


COLUMNS = ["상품명", "식재료 분류", "입력 방식", "영수증 분류", "영수증 메모", "수량", "단위", "보관 장소", "구매일", "기한", "메모"]
DB_FIELDS = ["name", "category", "source", "receipt_category", "receipt_ref", "quantity", "unit", "location", "purchase_date", "expiry_date", "memo"]


def editor_config():
    return {
        "식재료 분류": st.column_config.SelectboxColumn(options=names("categories"), required=True),
        "입력 방식": st.column_config.SelectboxColumn(options=SOURCES, required=True),
        "영수증 분류": st.column_config.SelectboxColumn(options=[""] + names("receipt_categories")),
        "단위": st.column_config.SelectboxColumn(options=UNITS, required=True),
        "보관 장소": st.column_config.SelectboxColumn(options=LOCATIONS, required=True),
        "수량": st.column_config.NumberColumn(min_value=0.001, max_value=1_000_000.0, required=True),
        "구매일": st.column_config.DateColumn(required=True),
        "기한": st.column_config.DateColumn(required=True),
    }


def change_stock(item_id, action, amount, reason):
    if action not in {"사용", "폐기"} or not 0 < amount <= 1_000_000:
        raise ValueError("처리 구분 또는 수량이 올바르지 않습니다.")
    with connect() as c:
        c.execute("BEGIN IMMEDIATE")
        item = c.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        if not item or amount > item["quantity"]:
            raise ValueError("현재 재고보다 많은 수량을 처리할 수 없습니다. 새로고침 후 확인해 주세요.")
        c.execute("UPDATE items SET quantity=MAX(0, ROUND(quantity-?, 9)) WHERE id=?", (amount, item_id))
        c.execute("INSERT INTO logs(item_id,item_name,action,quantity,unit,reason,created_at) VALUES(?,?,?,?,?,?,?)",
                  (item_id,item["name"],action,amount,item["unit"],reason,datetime.now().isoformat(timespec="seconds")))


def make_backup():
    with connect() as c:
        c.execute("BEGIN")
        data = {t: [dict(r) for r in c.execute(f"SELECT * FROM {t} ORDER BY id")]
                for t in ["categories", "receipt_categories", "items", "logs"]}
    return json.dumps({"version": 1, "exported_at": datetime.now().isoformat(), "data": data}, ensure_ascii=False, indent=2)


def restore_backup(raw):
    if len(raw) > 10_000_000:
        raise ValueError("백업은 10MB 이하여야 합니다.")
    obj = json.loads(raw)
    if obj.get("version") != 1 or not isinstance(obj.get("data"), dict):
        raise ValueError("지원하지 않는 백업 형식입니다.")
    data = obj["data"]
    specs = {
        "categories": ["id", "name"], "receipt_categories": ["id", "name"],
        "items": ["id"] + DB_FIELDS + ["created_at"],
        "logs": ["id", "item_id", "item_name", "action", "quantity", "unit", "reason", "created_at"]}
    for table, fields in specs.items():
        rows = data.get(table)
        if not isinstance(rows, list) or len(rows) > 100000:
            raise ValueError("백업 테이블이 잘못되었습니다.")
        for row in rows:
            if not isinstance(row, dict) or set(row) != set(fields):
                raise ValueError("백업의 필드가 일치하지 않습니다.")
    if not data["categories"] or not data["receipt_categories"]:
        raise ValueError("분류 목록이 비어 있습니다.")
    for item in data["items"]:
        quantity = float(item["quantity"])
        if not 0 <= quantity <= 1_000_000:
            raise ValueError("잘못된 재고 수량입니다.")
        date.fromisoformat(item["purchase_date"])
        date.fromisoformat(item["expiry_date"])
        if item["unit"] not in UNITS or item["location"] not in LOCATIONS:
            raise ValueError("잘못된 단위 또는 보관 장소입니다.")
    for log in data["logs"]:
        if log["action"] not in {"사용", "폐기"} or not 0 < float(log["quantity"]) <= 1_000_000:
            raise ValueError("잘못된 이력입니다.")
    with connect() as c:
        c.execute("BEGIN IMMEDIATE")
        c.execute("DELETE FROM logs")
        c.execute("DELETE FROM items")
        c.execute("DELETE FROM categories")
        c.execute("DELETE FROM receipt_categories")
        for table, fields in specs.items():
            sql = f"INSERT INTO {table}({','.join(fields)}) VALUES({','.join('?' for _ in fields)})"
            c.executemany(sql, [[r[k] for k in fields] for r in data[table]])




INGREDIENT_GROUPS = {'채소': ['애호박', '감자', '양파', '당근', '대파', '양배추', '오이', '시금치', '콩나물', '숙주', '브로콜리', '토마토', '깻잎', '배추', '고구마', '마늘'], '버섯': ['팽이버섯', '표고버섯', '새송이버섯'], '과일': ['사과', '바나나', '딸기', '귤', '배', '레몬'], '육류': ['돼지고기', '소고기', '닭고기', '베이컨', '햄', '소시지'], '생선·해산물': ['고등어', '연어', '오징어', '새우', '어묵', '멸치'], '달걀·두부': ['달걀', '두부', '순두부'], '유제품': ['우유', '치즈', '버터', '요거트'], '밥·면·곡류': ['밥', '쌀', '떡', '떡국떡', '소면', '파스타', '라면', '식빵', '밀가루'], '김치·반찬': ['김치', '김', '단무지'], '양념·소스': ['간장', '된장', '고추장', '고춧가루', '소금', '설탕', '식용유', '참기름', '식초', '굴소스', '케첩', '마요네즈', '국간장', '참치액', '후추'], '통조림·냉동': ['참치', '옥수수', '만두', '냉동볶음밥'], '기타': []}

RECIPES = [
    ("두부 애호박 된장국", ["두부", "애호박", "된장"], "물을 끓여 된장을 풀고 애호박과 두부를 넣어 충분히 익혀요."),
    ("두부 애호박 볶음", ["두부", "애호박", "간장", "식용유"], "물기를 뺀 두부를 굽고 애호박을 넣어 볶은 뒤 간장으로 간해요."),
    ("두부조림", ["두부", "간장", "마늘"], "두부를 굽고 간장·다진 마늘·물을 넣어 충분히 조려요."),
    ("애호박전", ["애호박", "달걀", "밀가루", "식용유"], "얇게 썬 애호박에 밀가루와 달걀물을 입혀 속까지 익혀요."),
    ("김치볶음밥", ["김치", "밥", "식용유"], "김치를 볶다가 밥을 넣고 골고루 충분히 볶아요."),
    ("달걀볶음밥", ["달걀", "밥", "대파", "식용유"], "대파를 볶고 달걀을 완전히 익힌 다음 밥을 넣어 볶아요."),
    ("감자양파볶음", ["감자", "양파", "식용유"], "가늘게 썬 감자와 양파를 기름에 볶아 충분히 익혀요."),
    ("참치김치찌개", ["참치", "김치", "두부"], "김치를 볶고 물과 참치를 넣어 끓인 뒤 두부를 넣어 익혀요."),
]

RECIPES.extend([('달걀찜', ['달걀', '소금'], '달걀에 물과 소금을 섞고 약한 불이나 중탕으로 중심까지 완전히 익혀요.'), ('달걀말이', ['달걀', '당근', '대파', '소금', '식용유'], '다진 채소를 달걀물에 섞어 얇게 부치며 말고 속까지 익혀요.'), ('간장달걀밥', ['밥', '달걀', '간장', '참기름'], '달걀을 완전히 익혀 따뜻한 밥 위에 올리고 간장과 참기름을 더해요.'), ('감자전', ['감자', '소금', '식용유'], '감자를 갈아 가라앉은 전분과 섞어 기름 두른 팬에 속까지 부쳐요.'), ('감자조림', ['감자', '간장', '설탕', '식용유'], '감자를 볶다가 물과 간장·설탕을 넣고 부드러워질 때까지 조려요.'), ('두부부침', ['두부', '식용유', '간장'], '두부 물기를 제거해 노릇하게 굽고 간장을 곁들여요.'), ('양배추달걀전', ['양배추', '달걀', '밀가루', '소금', '식용유'], '채 썬 양배추와 달걀·밀가루를 섞어 속까지 완전히 부쳐요.'), ('콩나물국', ['콩나물', '대파', '마늘', '국간장'], '콩나물을 물에 충분히 끓이고 마늘·대파·국간장으로 간해요.'), ('콩나물무침', ['콩나물', '마늘', '참기름', '소금'], '콩나물을 충분히 삶아 건지고 양념에 무쳐요.'), ('시금치무침', ['시금치', '마늘', '참기름', '소금'], '시금치를 데쳐 헹구고 물기를 짜 양념에 무쳐요.'), ('오이무침', ['오이', '고춧가루', '식초', '설탕', '소금'], '오이를 썰어 소금에 살짝 절이고 물기를 뺀 뒤 양념에 무쳐요.'), ('애호박볶음', ['애호박', '양파', '마늘', '식용유', '소금'], '채소를 썰어 기름에 볶고 마늘과 소금으로 간해요.'), ('팽이버섯달걀전', ['팽이버섯', '달걀', '소금', '식용유'], '잘게 자른 버섯과 달걀을 섞어 버섯과 달걀이 모두 충분히 익도록 부쳐요.'), ('버섯볶음', ['새송이버섯', '양파', '간장', '식용유'], '버섯과 양파를 썰어 볶다가 간장으로 간해요.'), ('김치전', ['김치', '밀가루', '식용유'], '김치와 밀가루·물을 섞어 반죽하고 얇게 펼쳐 속까지 부쳐요.'), ('김치두부국', ['김치', '두부', '대파'], '김치를 물에 끓인 뒤 두부와 대파를 넣어 익혀요.'), ('돼지고기김치찌개', ['돼지고기', '김치', '두부', '마늘'], '돼지고기와 김치를 볶다가 물을 넣고 고기가 속까지 익도록 끓여요.'), ('된장찌개', ['된장', '두부', '애호박', '감자', '양파', '마늘'], '물에 된장을 풀고 감자를 먼저 넣은 뒤 나머지 재료를 넣어 익혀요.'), ('소고기뭇국', ['소고기', '무', '국간장', '마늘', '참기름'], '소고기와 무를 볶아 물을 붓고 고기가 충분히 익도록 끓여요.'), ('어묵국', ['어묵', '무', '대파', '국간장'], '무를 먼저 끓이고 어묵과 대파를 넣어 충분히 끓여 간해요.'), ('떡국', ['떡국떡', '달걀', '대파', '국간장'], '물에 떡을 넣어 부드러워질 때까지 끓이고 달걀을 넣어 완전히 익혀요.'), ('만둣국', ['만두', '달걀', '대파', '국간장'], '만두를 제품 조리법대로 속까지 익히고 달걀과 대파를 넣어 끓여요.'), ('떡볶이', ['떡', '어묵', '고추장', '설탕', '대파'], '물에 고추장과 설탕을 풀고 떡과 어묵을 넣어 부드러워질 때까지 끓여요.'), ('간장떡볶이', ['떡', '간장', '설탕', '양파', '식용유'], '떡을 부드럽게 데친 뒤 양파와 볶다가 간장·설탕·물을 넣어 조려요.'), ('참치마요덮밥', ['밥', '참치', '달걀', '마요네즈', '간장'], '달걀을 완전히 익혀 밥과 참치 위에 올리고 마요네즈와 간장을 더해요.'), ('채소볶음밥', ['밥', '당근', '양파', '대파', '식용유', '소금'], '잘게 썬 채소를 볶고 밥을 넣어 골고루 볶아 간해요.'), ('새우볶음밥', ['밥', '새우', '달걀', '대파', '식용유', '소금'], '새우와 달걀을 완전히 익힌 뒤 밥과 대파를 넣어 볶아요.'), ('햄볶음밥', ['밥', '햄', '양파', '당근', '식용유'], '햄과 채소를 볶다가 밥을 넣어 충분히 볶아요.'), ('닭고기덮밥', ['닭고기', '밥', '양파', '간장', '설탕'], '닭고기를 양파·양념·물과 함께 속까지 충분히 익혀 밥에 올려요.'), ('제육볶음', ['돼지고기', '양파', '대파', '고추장', '간장', '설탕', '마늘'], '고기와 양념을 섞어 채소와 함께 고기가 속까지 완전히 익도록 볶아요.'), ('소고기불고기', ['소고기', '양파', '대파', '간장', '설탕', '마늘'], '고기에 양념과 채소를 섞어 고기가 충분히 익을 때까지 볶아요.'), ('간장닭조림', ['닭고기', '감자', '간장', '설탕', '마늘'], '닭고기와 감자에 양념과 물을 넣고 닭고기 중심까지 완전히 익도록 조려요.'), ('오징어볶음', ['오징어', '양파', '대파', '고추장', '간장', '식용유'], '손질한 오징어와 채소를 양념에 볶아 충분히 익혀요.'), ('어묵볶음', ['어묵', '양파', '간장', '설탕', '식용유'], '어묵과 양파를 볶다가 간장·설탕·물을 넣고 익혀요.'), ('소시지채소볶음', ['소시지', '양파', '케첩', '식용유'], '소시지를 제품 조리법대로 익힌 뒤 양파와 케첩을 넣어 볶아요.'), ('고등어구이', ['고등어', '소금', '식용유'], '손질한 고등어에 소금을 뿌리고 기름 두른 팬에서 속까지 충분히 익혀요.'), ('연어구이', ['연어', '소금', '버터'], '연어에 소금을 뿌리고 버터를 두른 팬에서 중심까지 완전히 익혀요.'), ('새우마늘볶음', ['새우', '마늘', '식용유', '소금'], '마늘을 볶다가 손질한 새우를 넣어 속까지 완전히 익혀요.'), ('브로콜리달걀볶음', ['브로콜리', '달걀', '식용유', '소금'], '브로콜리를 데친 뒤 달걀과 볶아 달걀을 완전히 익혀요.'), ('옥수수치즈구이', ['옥수수', '치즈', '마요네즈', '버터'], '옥수수와 마요네즈를 섞어 버터 두른 팬에 넣고 치즈를 덮어 녹여요.'), ('양배추샐러드', ['양배추', '당근', '마요네즈', '식초'], '깨끗이 씻은 채소를 채 썰어 마요네즈와 식초에 버무려요.'), ('감자샐러드', ['감자', '달걀', '오이', '마요네즈', '소금'], '감자와 달걀을 완전히 익혀 으깨고 오이와 마요네즈를 넣어 섞어요.'), ('달걀샌드위치', ['식빵', '달걀', '마요네즈', '소금'], '완전히 삶은 달걀을 으깨 마요네즈에 섞고 식빵 사이에 넣어요.'), ('프렌치토스트', ['식빵', '달걀', '우유', '버터'], '달걀과 우유를 섞어 식빵을 적시고 버터 두른 팬에서 달걀물이 속까지 익도록 구워요.'), ('치즈토스트', ['식빵', '치즈', '버터'], '식빵 사이에 치즈를 넣고 버터 두른 팬에서 앞뒤로 구워요.'), ('바나나요거트볼', ['바나나', '요거트'], '바나나를 썰어 요거트 위에 올려요.'), ('과일요거트', ['사과', '바나나', '요거트'], '깨끗이 씻고 손질한 과일을 잘라 요거트에 섞어요.'), ('김치소면', ['소면', '김치', '고추장', '식초', '설탕', '참기름'], '소면을 제품 조리법대로 삶아 찬물에 헹구고 김치와 양념에 비벼요.'), ('간장비빔국수', ['소면', '간장', '설탕', '참기름'], '소면을 삶아 헹군 뒤 간장·설탕·참기름으로 비벼요.'), ('마늘파스타', ['파스타', '마늘', '식용유', '소금'], '면을 삶고 마늘을 기름에 볶은 뒤 면과 면수를 넣어 섞어요.'), ('두부채소전', ['두부', '양파', '애호박', '팽이버섯', '달걀', '소금', '식용유'], '물기를 뺀 두부와 잘게 다진 채소·달걀을 섞고 팬에서 양면과 속까지 충분히 익혀요.'), ('애호박감자국', ['감자', '애호박', '두부', '대파', '국간장', '참치액', '소금', '후추'], '감자와 애호박을 육수에 끓이고 감자가 익으면 두부와 양념을 넣어 한소끔 끓여요. 육수는 별도 준비해요.'), ('감자고추장찌개', ['감자', '애호박', '양파', '두부', '대파', '된장', '고추장', '마늘'], '육수에 된장과 고추장을 풀고 감자부터 끓인 뒤 나머지 채소와 두부를 넣어 익혀요. 육수는 별도 준비해요.')])


def korea_today():
    return datetime.now(timezone(timedelta(hours=9))).date()


def ingredient_key(name):
    key = ''.join(str(name).split()).casefold()
    return {"계란": "달걀", "파": "대파", "찬밥": "밥", "쌀밥": "밥", "계란후라이": "계란후라이"}.get(key, key)


def recipe_matches(items, today):
    # Exact normalized ingredient names only; never treat expired stock as available.
    available = {ingredient_key(i['name']) for i in items
                 if i['quantity'] > 0 and date.fromisoformat(i['expiry_date']) >= today}
    results = []
    for title, ingredients, steps in RECIPES:
        have = [x for x in ingredients if ingredient_key(x) in available]
        missing = [x for x in ingredients if ingredient_key(x) not in available]
        if have:
            results.append(dict(title=title, have=have, missing=missing,
                                score=len(have)/len(ingredients), steps=steps))
    return sorted(results, key=lambda r: (-r['score'], -len(r['have']), r['title']))


initialize()
# Additive migration: retain every existing category and all inventory records.
with connect() as conn:
    conn.executemany("INSERT OR IGNORE INTO categories(name) VALUES(?)", [(n,) for n in INGREDIENT_GROUPS])
st.html('<div class="nb-home">'+brand_logo()+'</div>')
st.html("""
<section class="bbyok-hero" aria-label="냉장뾱 소개">
  <div class="eyebrow">FRESH TOGETHER</div>
  <div class="headline">냉장고 속 신선함,<br>우리 가족과 뾱!</div>
  <div class="sub">함께 채우고 · 맛있게 요리하고 · 잊기 전에 확인해요</div>
  <div class="bbyok-produce" aria-hidden="true"><span>🥦</span><span>🍋</span><span>🥕</span><span>🥑</span><span>🍅</span></div>
</section>
""")
st.caption("가족과 같은 냉장고를 보고, 남은 재료로 요리를 찾아보세요.")
st.info("👨‍👩‍👧‍👦 가족 공유: 가족에게 같은 앱 주소를 보내세요. 같은 서버의 목록을 함께 사용하며 아래 목록은 10초마다 갱신됩니다.")
st.caption("주의: 로그인·초대코드가 없는 방식입니다. 앱에 접속할 수 있는 사람은 누구나 재고를 보고 수정할 수 있어요.")
if 'notice' in st.session_state:
    st.success(st.session_state.pop('notice'))

if "screen" not in st.session_state:
    st.session_state["screen"] = "🧊 냉장고"
if "alert_days" not in st.session_state:
    st.session_state["alert_days"] = 3

def go_screen(target):
    st.session_state["screen"] = target

st.html("""<style>
.st-key-app_nav [data-testid="stHorizontalBlock"] {display:flex!important;flex-wrap:nowrap!important;gap:5px!important;}
.st-key-app_nav [data-testid="stColumn"] {flex:1 1 0!important;width:auto!important;min-width:0!important;}
.st-key-app_nav button {width:100%;min-height:60px!important;padding:7px 2px!important;border-radius:15px!important;}
.st-key-app_nav button p {font-size:12px!important;white-space:normal;}
</style>""")
with st.container(key="app_nav"):
    buttons = st.columns(5)
    for col, target in zip(buttons, ["🧊 냉장고", "➕ 추가", "🍳 요리", "🔔 알림", "⚙️ 설정"]):
        col.button(target, key="nav_"+target, use_container_width=True,
                   type="primary" if st.session_state["screen"] == target else "secondary",
                   on_click=go_screen, args=(target,))
screen = st.session_state["screen"]
days = st.session_state["alert_days"]

if screen == "⚙️ 설정":
    with st.expander("⚙️ 설정 · 백업", expanded=False):
        st.number_input("기한 며칠 전부터 알려줄까요?", 0, 30, key="alert_days")
        st.download_button("전체 데이터 백업", make_backup(), "fridge_backup.json", "application/json")
        st.caption("기존 앱과 같은 데이터베이스·백업 형식을 사용합니다. 클라우드 재배포 전에 백업하세요.")
        uploaded = st.file_uploader("백업 복원", type=['json'])
        confirmed = st.checkbox("복원하면 현재 데이터가 백업 내용으로 교체됨을 확인했어요")
        if st.button("복원하기", disabled=not (uploaded and confirmed)):
            try:
                restore_backup(uploaded.getvalue())
                st.session_state.notice = "백업을 복원했어요."
                st.rerun()
            except (ValueError, KeyError, TypeError, sqlite3.Error) as e:
                st.error(str(e))

if screen == "➕ 추가":
    st.subheader("➕ 재료 등록")
    st.caption("자주 쓰는 재료는 버튼으로 선택하고 기한만 확인하세요.")
    selected_category = st.selectbox("① 재료 카테고리", names("categories"), key="add_category")
    quick = INGREDIENT_GROUPS.get(selected_category, [])
    for base in range(0, len(quick), 3):
        cols = st.columns(3)
        for col, value in zip(cols, quick[base:base+3]):
            if col.button(value, key="quick_"+value, use_container_width=True):
                st.session_state["ingredient_name"] = value
    with st.expander("➕ 내 카테고리 만들기"):
        custom_category = st.text_input("새 카테고리 이름", max_chars=40)
        if st.button("카테고리 추가", use_container_width=True):
            if custom_category.strip():
                with connect() as conn:
                    conn.execute("INSERT OR IGNORE INTO categories(name) VALUES(?)", (custom_category.strip(),))
                st.rerun()
            else:
                st.warning("이름을 입력해 주세요.")
    with st.form("add", clear_on_submit=True):
        name = st.text_input("재료 이름", placeholder="버튼으로 선택하거나 직접 입력", key="ingredient_name")
        a,b = st.columns(2)
        expiry = a.date_input("제품에 표시된 기한", date.today()+timedelta(days=7))
        quantity = b.number_input("수량", min_value=0.001, max_value=1000000.0, value=1.0, step=1.0)
        with st.expander("추가 정보 (선택)"):
            a,b,c = st.columns(3)
            unit = a.selectbox("단위", UNITS)
            location = b.selectbox("보관 장소", LOCATIONS)
            category = selected_category
            c.caption("분류: " + category)
            source = st.selectbox("입력 방식", SOURCES)
            receipt = st.selectbox("구매처 · 영수증 분류", names('receipt_categories'))
        submitted = st.form_submit_button("등록하기", type="primary", use_container_width=True)
        if submitted:
            try:
                clean_name = valid_text(name, '재료 이름')
                with connect() as conn:
                    conn.execute("INSERT INTO items (" + ','.join(DB_FIELDS) + ",created_at) VALUES (" + ','.join(['?']*12) + ")", (clean_name, category, source, receipt if source==SOURCES[1] else '', '', quantity, unit, location, date.today().isoformat(), expiry.isoformat(), '', datetime.now().isoformat(timespec='seconds')))
                st.session_state.notice = f"{clean_name} 등록 완료!"
                st.session_state["screen"] = "🧊 냉장고"
                st.rerun()
            except (ValueError, sqlite3.Error) as e:
                st.error(str(e))

@st.fragment(run_every="10s")
def shared_fridge():
    items = [i for i in records('items') if i['quantity']>0]
    today = korea_today()
    items.sort(key=lambda i:(i['expiry_date'],i['id']))
    overdue = [i for i in items if date.fromisoformat(i['expiry_date'])<today]
    soon = [i for i in items if 0 <= (date.fromisoformat(i['expiry_date'])-today).days <= days]
    if screen == "🔔 알림":
        st.subheader("🔔 오늘의 요약")
        attention = overdue + soon
        summary = f"오늘 확인할 재료 {len(attention)}개 · 기한 지남 {len(overdue)}개 · 기한 임박 {len(soon)}개"
        st.write(summary)
        # Browser-local storage remembers the day across reconnects on this device.
        # JSON encoding prevents ingredient names from becoming executable markup.
        import streamlit.components.v1 as components
        payload = json.dumps({"day": today.isoformat(), "text": summary}, ensure_ascii=True)
        components.html("""<div id="digest" style="font:14px sans-serif"></div><script>
        const d = """ + payload + """;
        let fresh = true;
        try { const k='fridge-digest-v1'; fresh=localStorage.getItem(k)!==d.day;
        localStorage.setItem(k,d.day); } catch(e) { fresh=false; }
        if(fresh) { document.getElementById('digest').textContent='🔔 '+d.text; }
        </script>""", height=40)
        with st.expander("요약 상세 보기"):
            for i in attention:
                label = "기한 지남" if date.fromisoformat(i['expiry_date']) < today else "기한 임박"
                st.write(f"{i['name']} · {label} · {i['expiry_date']}")
            if not attention:
                st.caption("오늘 확인할 재료가 없어요.")
    if screen == "🍳 요리":
        with st.expander("🍳 남은 재료로 요리 찾기", expanded=True):
            st.caption(f"요리 {len(RECIPES)}종과 비교해요. 양념도 등록해야 보유한 것으로 표시하며, 기한이 지난 재료는 제외해요. 수량·인분은 계산하지 않는 간단 메뉴 아이디어입니다. 물·별도 안내한 육수는 직접 준비하세요.")
            menu_query = st.text_input("요리 이름 검색", placeholder="예: 전, 볶음밥, 국")
            only_ready = st.checkbox("등록된 재료가 모두 갖춰진 메뉴만")
            max_results = st.select_slider("추천 개수", options=[10, 20, 40, len(RECIPES)], value=20)
            st.caption("참고: 만개의레시피 두부전·감자고추장찌개, Cookbrief 애호박감자국. 아래 조리 안내는 직접 작성한 요약이며 상세 계량 레시피가 아닙니다.")
            st.markdown("[두부전 참고](https://www.10000recipe.com/recipe/6994053) · [고추장찌개 참고](https://www.10000recipe.com/recipe/6921095) · [애호박감자국 참고](https://cookbrief.com/r/zxfhqb/aehobakgamjaguk)")
            suggestions = recipe_matches(items, today)
            if not suggestions:
                st.write("두부, 애호박, 달걀 등 재료를 등록하면 요리를 추천해요.")
            suggestions = [r for r in suggestions if menu_query.strip() in r['title'] and (not only_ready or not r['missing'])]
            if not suggestions:
                st.info("조건에 맞는 추천이 없어요. 재료를 추가하거나 검색·필터를 바꿔 보세요.")
            for r in suggestions[:max_results]:
                st.markdown(f"**{r['title']}** · 재료 일치 {len(r['have'])}/{len(r['have'])+len(r['missing'])}")
                st.write("있는 재료: " + ', '.join(r['have']))
                st.write("더 필요한 재료: " + (', '.join(r['missing']) or "없음"))
                st.caption(r['steps'])
    if screen == "🧊 냉장고":
        st.subheader(f"🧊 냉장고 재료 {len(items)}종")
        search = st.text_input("재료 검색", placeholder="찾는 재료 이름")
        if not items:
            st.info("냉장고가 비어 있어요. ➕ 추가 버튼을 눌러 첫 재료를 등록해 보세요.")
        for item in items:
            if search.strip().casefold() not in item['name'].casefold():
                continue
            diff = (date.fromisoformat(item['expiry_date'])-today).days
            badge = f"🔴 {abs(diff)}일 지남" if diff<0 else ('🟠 오늘까지' if diff==0 else f"{'🟡' if diff<=days else '🟢'} {diff}일 남음")
            with st.container(border=True):
                st.markdown(f"**{item['name']}** · {item['quantity']:g}{item['unit']}")
                st.caption(f"{badge} | {item['expiry_date']} | {item['location']}")
                a,b = st.columns(2)
                if a.button("✅ 전부 사용", key=f"use{item['id']}", use_container_width=True):
                    try:
                        change_stock(item['id'],'사용',item['quantity'],'')
                        st.session_state.notice = '사용 기록을 저장했어요.'
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                with b.popover("수정 · 일부 사용 · 폐기", use_container_width=True):
                    with st.form(f"manage{item['id']}"):
                        new_name = st.text_input("재료 이름", item['name'])
                        new_date = st.date_input("기한", date.fromisoformat(item['expiry_date']))
                        action = st.selectbox("할 일", ['정보 수정','일부 사용','폐기'])
                        count_units = {"개", "봉", "팩", "병"}
                        stock = round(float(item['quantity']), 9)
                        if item['unit'] in count_units and stock.is_integer():
                            amount = st.number_input("처리 수량 (사용·폐기할 때)", min_value=1,
                                max_value=int(stock), value=1, step=1, format="%d", key=f"amount_count_{item['id']}_{stock}")
                            st.caption(f"{int(stock)}{item['unit']} 중 처리할 개수예요. − / + 버튼으로 1개씩 바꿔요.")
                        elif item['unit'] in count_units:
                            # Preserve legacy fractional inventory instead of silently rounding it.
                            amount = st.number_input("처리 수량 (사용·폐기할 때)", min_value=0.001,
                                max_value=stock, value=min(1.0, stock), step=1.0, format="%.3f",
                                key=f"amount_legacy_{item['id']}_{stock}")
                            st.caption("이전에 소수로 저장된 재고예요. 버튼은 1씩 바뀌며, 남은 소수 재고는 ‘전부 사용’으로 정리할 수 있어요.")
                        else:
                            amount = st.number_input("처리 수량 (사용·폐기할 때)", min_value=0.001,
                                max_value=stock, value=min(1.0, stock), step=0.1, format="%.3f",
                                key=f"amount_measure_{item['id']}_{stock}")
                            st.caption(f"단위: {item['unit']} · 무게와 부피는 소수로 입력할 수 있어요.")
                        if st.form_submit_button("적용"):
                            try:
                                if action=='정보 수정':
                                    cleaned = valid_text(new_name,'재료 이름')
                                    with connect() as conn:
                                        conn.execute('UPDATE items SET name=?, expiry_date=? WHERE id=?',(cleaned,new_date.isoformat(),item['id']))
                                else:
                                    change_stock(item['id'],'사용' if action=='일부 사용' else '폐기',amount,'')
                                st.session_state.notice = '저장했어요.'
                                st.rerun()
                            except (ValueError, sqlite3.Error) as e:
                                st.error(str(e))
        with st.expander("📋 사용 · 폐기 기록"):
            logs = list(reversed(records('logs')))
            if logs:
                df = pd.DataFrame(logs)[['created_at','item_name','action','quantity','unit']]
                df.columns = ['처리 시간','재료','구분','수량','단위']
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.caption('아직 기록이 없어요.')

if screen in {"🧊 냉장고", "🍳 요리", "🔔 알림"}:
    shared_fridge()
st.caption("하루 요약은 앱을 열었을 때 이 기기의 브라우저에서 표시됩니다. 이메일·휴대폰 푸시가 아니며 브라우저 저장 차단 시 자동 알림은 표시하지 않습니다. 기한만으로 섭취 안전성을 보장하지 않습니다.")
st.caption("로그인 없는 공유 앱은 방문자들이 같은 재고를 봅니다. 클라우드 로컬 저장은 유실될 수 있으며 GitHub에 데이터가 자동 저장되지는 않습니다.")
