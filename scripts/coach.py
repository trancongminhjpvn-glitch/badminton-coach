import os
import json
import re
import requests
from datetime import date

# â”€â”€ ç’°å¢ƒå¤‰æ•° â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
NOTION_TOKEN      = os.environ["NOTION_TOKEN"]
GITHUB_TOKEN      = os.environ["GITHUB_TOKEN"]
REPO              = os.environ["GITHUB_REPOSITORY"]
ISSUE_NUMBER      = os.environ["ISSUE_NUMBER"]
ISSUE_BODY        = os.environ["ISSUE_BODY"]

# â”€â”€ Notion DB IDs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
DB = {
    "é£Ÿäº‹è¨˜éŒ²":    "378acc4d-a5fa-8149-b472-d8a61436bf39",
    "ãƒ¬ã‚·ãƒ”å¸³":    "378acc4d-a5fa-81cf-afe1-f13f983987d6",
    "ç·´ç¿’è¨˜éŒ²":    "378acc4d-a5fa-81b8-88f4-ce03ee20ae32",
    "é€±æ¬¡ã‚µãƒžãƒªãƒ¼":"378acc4d-a5fa-810d-8480-cbb6946b7b48",
    "é£Ÿå“ãƒžã‚¹ã‚¿ãƒ¼":"378acc4d-a5fa-8136-900c-e9121e02db1d",
}

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

SYSTEM_PROMPT = """
ã‚ãªãŸã¯ãƒãƒ‰ãƒŸãƒ³ãƒˆãƒ³é¸æ‰‹ï¼ˆ65kg/163cmï¼‰å°‚å±žã®æ „é¤Šã‚³ãƒ¼ãƒã§ã™ã€‚

ã€æ „é¤Šç›®æ¨™ï¼ˆ65kgåŸºæº–ï¼‰ã€‘
- éžç·´ç¿’æ—¥ï¼š2,100kcalï½œP:104gï½œC:260gï½œF:58g
- ç·´ç¿’æ—¥(2h)ï¼š2,700kcalï½œP:117gï½œC:390gï½œF:60g
- ç·´ç¿’æ—¥(6h)ï¼š3,800kcalï½œP:130gï½œC:520gï½œF:84g

ã€ç¢ºå®šæ¸ˆã¿é£Ÿå“ãƒžã‚¹ã‚¿ãƒ¼ï¼ˆ100gã‚ãŸã‚Šï¼‰ã€‘
- ã‚ªãƒ¼ãƒˆãƒŸãƒ¼ãƒ«(ãƒ‰ãƒ³ã‚­)ï¼š380kcal P13.3g F6.7g C66.7g
- X-Plosion ãƒ—ãƒ­ãƒ†ã‚¤ãƒ³(ãƒŸãƒ«ã‚¯ãƒãƒ§ã‚³)ï¼š387kcal P71.7g F6.7g C12.3g â€»30gä½¿ç”¨æ™‚:116kcal P21.5g F2g C3.7g
- ãƒãƒŠãƒŠ(çš®ãªã—)ï¼š86kcal P1.1g F0.2g C22.5g
- é¶åµ(å…¨åµ)ï¼š151kcal P12.3g F10.3g C0.3g â€»1å€‹50g
- ç‰›ä¹³(ç„¡èª¿æ•´)ï¼š67kcal P3.3g F3.8g C4.8g
- é¶ã‚€ã­è‚‰(çš®ãªã—ãƒ»ç”Ÿ)ï¼š116kcal P23.3g F1.9g C0g
- è‡ªå®¶ãƒ¯ãƒƒãƒ•ãƒ«(1å€‹)ï¼š220kcal P10.3g F6.1g C31.6g

ã€å…¥åŠ›ã®ç¨®åˆ¥åˆ¤å®šã€‘
- ã€Œé£Ÿäº‹ã€ã€Œæœã€ã€Œæ˜¼ã€ã€Œå¤œã€ã€Œé–“é£Ÿã€â†’ é£Ÿäº‹è¨˜éŒ²ãƒ¢ãƒ¼ãƒ‰
- ã€Œç·´ç¿’ã€ã€Œãƒˆãƒ¬ãƒ¼ãƒ‹ãƒ³ã‚°ã€ã€Œãƒãƒ‰ãƒŸãƒ³ãƒˆãƒ³ã€â†’ ç·´ç¿’è¨˜éŒ²ãƒ¢ãƒ¼ãƒ‰
- ã€Œãƒ¬ã‚·ãƒ”ã€ã€Œææ–™ã€ã€Œä½œã£ãŸã€â†’ ãƒ¬ã‚·ãƒ”ãƒ¢ãƒ¼ãƒ‰

ã€å›žç­”ãƒ«ãƒ¼ãƒ«ã€‘
1. æ „é¤Šè¨ˆç®—ã¯å¿…ãšæ•°å€¤ã§å‡ºã™
2. ç›®æ¨™å€¤ã¨ã®æ¯”è¼ƒã‚’é”æˆçŽ‡ã§ç¤ºã™ï¼ˆðŸŸ©ðŸŸ¨ðŸŸ¥ï¼‰
3. ä¸è¶³æ „é¤Šç´ ã¯å…·ä½“çš„ãªé£Ÿå“ã§è£œã„æ–¹ã‚’ææ¡ˆ
4. æ¬¡ã®ç·´ç¿’ã«å‘ã‘ãŸã‚¢ãƒ‰ãƒã‚¤ã‚¹ã‚’1ã¤æ·»ãˆã‚‹
5. æœ€å¾Œã«å¿…ãšJSONå½¢å¼ã§Notionä¿å­˜ç”¨ãƒ‡ãƒ¼ã‚¿ã‚’å‡ºåŠ›ã™ã‚‹

ã€JSONå‡ºåŠ›ãƒ•ã‚©ãƒ¼ãƒžãƒƒãƒˆã€‘
é£Ÿäº‹è¨˜éŒ²ã®å ´åˆ:
```json
{
  "type": "é£Ÿäº‹è¨˜éŒ²",
  "date": "YYYY-MM-DD",
  "content": "é£Ÿäº‹å†…å®¹ã®è¦ç´„ï¼ˆè¿½è¨˜åˆ†ã®ã¿ï¼‰",
  "kcal": æ•°å€¤,
  "protein": æ•°å€¤,
  "carbs": æ•°å€¤,
  "fat": æ•°å€¤,
  "is_practice_day": true/false,
  "memo": "ã‚¢ãƒ‰ãƒã‚¤ã‚¹"
}
```

ç·´ç¿’è¨˜éŒ²ã®å ´åˆ:
```json
{
  "type": "ç·´ç¿’è¨˜éŒ²",
  "date": "YYYY-MM-DD",
  "content": "ç·´ç¿’å†…å®¹",
  "duration_min": æ•°å€¤,
  "kcal_burned": æ•°å€¤,
  "load_level": "ä½Ž/ä¸­/é«˜/æœ€é«˜",
  "fatigue": æ•°å€¤,
  "recovery_advice": "å›žå¾©ã‚¢ãƒ‰ãƒã‚¤ã‚¹",
  "video_url": "URLã¾ãŸã¯null",
  "video_memo": "ãƒ¡ãƒ¢ã¾ãŸã¯null"
}
```

ãƒ¬ã‚·ãƒ”ã®å ´åˆ:
```json
{
  "type": "ãƒ¬ã‚·ãƒ”",
  "name": "ãƒ¬ã‚·ãƒ”å",
  "ingredients": "ææ–™ãƒ»åˆ†é‡",
  "kcal_per_serving": æ•°å€¤,
  "protein": æ•°å€¤,
  "carbs": æ•°å€¤,
  "fat": æ•°å€¤,
  "rating": "â—Ž å„ªç§€/â—‹ è‰¯å¥½/â–³ è¦æ”¹å–„",
  "memo": "è©•ä¾¡ã‚³ãƒ¡ãƒ³ãƒˆ"
}
```
""".strip()


# â”€â”€ å½“æ—¥ã®ç´¯è¨ˆã‚’Notionã‹ã‚‰å–å¾— â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def get_today_totals(target_date: str) -> dict:
    """å½“æ—¥ã®é£Ÿäº‹è¨˜éŒ²ç´¯è¨ˆã‚’è¿”ã™ã€‚ãƒ¬ã‚³ãƒ¼ãƒ‰ãªã‘ã‚Œã°å…¨ã¦0"""
    existing = find_today_meal_record(target_date)
    if not existing:
        return {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0,
                "content": "", "is_practice_day": False}
    props = existing["properties"]
    content_rt = props.get("é£Ÿäº‹å†…å®¹", {}).get("rich_text", [])
    return {
        "kcal":           props.get("ã‚«ãƒ­ãƒªãƒ¼(kcal)", {}).get("number") or 0,
        "protein":        props.get("ã‚¿ãƒ³ãƒ‘ã‚¯è³ª(g)",  {}).get("number") or 0,
        "carbs":          props.get("ç‚­æ°´åŒ–ç‰©(g)",    {}).get("number") or 0,
        "fat":            props.get("è„‚è³ª(g)",        {}).get("number") or 0,
        "content":        content_rt[0]["text"]["content"] if content_rt else "",
        "is_practice_day":props.get("ç·´ç¿’æ—¥", {}).get("checkbox", False),
    }


# â”€â”€ Claude API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def ask_claude(user_message: str, today_totals: dict, target_date: str) -> str:
    # ç·´ç¿’æ—¥ã‹ã©ã†ã‹ã§ç›®æ¨™å€¤ã‚’åˆ‡ã‚Šæ›¿ãˆ
    is_practice = today_totals["is_practice_day"]
    goal_kcal    = 2700  if is_practice else 2100
    goal_protein = 117   if is_practice else 104
    goal_carbs   = 390   if is_practice else 260
    goal_fat     = 60    if is_practice else 58

    # æ®‹ã‚Š = ç›®æ¨™ - ç´¯è¨ˆï¼ˆè¿½è¨˜åˆ†ã‚’è¨ˆç®—ã™ã‚‹å‰ã®çŠ¶æ…‹ï¼‰
    rem_kcal    = max(0, goal_kcal    - today_totals["kcal"])
    rem_protein = max(0, goal_protein - today_totals["protein"])
    rem_carbs   = max(0, goal_carbs   - today_totals["carbs"])
    rem_fat     = max(0, goal_fat     - today_totals["fat"])

    context = f"""
ã€{target_date} ã®å½“æ—¥ç´¯è¨ˆï¼ˆä»Šå›žã®å…¥åŠ›ã‚’åŠ ç®—ã™ã‚‹å‰ï¼‰ã€‘
- ã‚«ãƒ­ãƒªãƒ¼ï¼š{today_totals['kcal']} kcalï¼ˆç›®æ¨™ {goal_kcal} kcalï¼‰
- ã‚¿ãƒ³ãƒ‘ã‚¯è³ªï¼š{today_totals['protein']}gï¼ˆç›®æ¨™ {goal_protein}gï¼‰
- ç‚­æ°´åŒ–ç‰©ï¼š{today_totals['carbs']}gï¼ˆç›®æ¨™ {goal_carbs}gï¼‰
- è„‚è³ªï¼š{today_totals['fat']}gï¼ˆç›®æ¨™ {goal_fat}gï¼‰
- ã“ã‚Œã¾ã§ã®é£Ÿäº‹ï¼š{today_totals['content'] or 'ãªã—'}
- ç·´ç¿’æ—¥ï¼š{'ã¯ã„' if is_practice else 'ã„ã„ãˆ'}

ã€ä»Šå›žåŠ ç®—å‰ã®æ®‹ã‚Šå¿…è¦é‡ã€‘
- ã‚«ãƒ­ãƒªãƒ¼ï¼šæ®‹ã‚Š {rem_kcal} kcal
- ã‚¿ãƒ³ãƒ‘ã‚¯è³ªï¼šæ®‹ã‚Š {rem_protein}g
- ç‚­æ°´åŒ–ç‰©ï¼šæ®‹ã‚Š {rem_carbs}g
- è„‚è³ªï¼šæ®‹ã‚Š {rem_fat}g

---
ä»Šå›žã®å…¥åŠ›ï¼š
{user_message}
"""

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-opus-4-5",
            "max_tokens": 2048,
            "system": SYSTEM_PROMPT + "\n\nã€è¿½åŠ ãƒ«ãƒ¼ãƒ«ã€‘å›žç­”ã®æœ€å¾Œã«ã€ŒðŸ“Š æœ¬æ—¥ã®æ®‹ã‚Šç›®æ¨™ã€ã‚»ã‚¯ã‚·ãƒ§ãƒ³ã‚’å¿…ãšè¿½åŠ ã™ã‚‹ã€‚ä»Šå›žã®é£Ÿäº‹ã‚’åŠ ç®—ã—ãŸå¾Œã®æ®‹ã‚Šå¿…è¦é‡ï¼ˆã‚«ãƒ­ãƒªãƒ¼ãƒ»Pãƒ»Fãƒ»Cï¼‰ã‚’è¡¨ç¤ºã—ã€æ®‹ã‚Šã‚’æº€ãŸã™ãŸã‚ã®å…·ä½“çš„ãªé£Ÿå“ä¾‹ã‚’1ã€œ2å€‹ææ¡ˆã™ã‚‹ã“ã¨ã€‚",
            "messages": [{"role": "user", "content": context}],
        },
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def extract_json(text: str) -> dict | None:
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


# â”€â”€ Notion: å½“æ—¥ã®é£Ÿäº‹è¨˜éŒ²ã‚’æ¤œç´¢ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def find_today_meal_record(target_date: str) -> dict | None:
    """æŒ‡å®šæ—¥ä»˜ã®é£Ÿäº‹è¨˜éŒ²ãƒšãƒ¼ã‚¸ã‚’æ¤œç´¢ã—ã¦è¿”ã™"""
    body = {
        "filter": {
            "property": "æ—¥ä»˜",
            "title": {"equals": target_date}
        }
    }
    resp = requests.post(
        f"https://api.notion.com/v1/databases/{DB['é£Ÿäº‹è¨˜éŒ²']}/query",
        headers=NOTION_HEADERS,
        json=body,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None


def find_today_practice_record(target_date: str) -> dict | None:
    """æŒ‡å®šæ—¥ä»˜ã®ç·´ç¿’è¨˜éŒ²ãƒšãƒ¼ã‚¸ã‚’æ¤œç´¢ã—ã¦è¿”ã™"""
    body = {
        "filter": {
            "property": "æ—¥ä»˜",
            "title": {"equals": target_date}
        }
    }
    resp = requests.post(
        f"https://api.notion.com/v1/databases/{DB['ç·´ç¿’è¨˜éŒ²']}/query",
        headers=NOTION_HEADERS,
        json=body,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None


# â”€â”€ Notion: ä¿å­˜ãƒ»æ›´æ–° â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def save_to_notion(data: dict) -> str:
    """ãƒ‡ãƒ¼ã‚¿ã‚’Notionã«ä¿å­˜ã€‚é£Ÿäº‹ãƒ»ç·´ç¿’ã¯å½“æ—¥ãƒ¬ã‚³ãƒ¼ãƒ‰ã‚’æ¤œç´¢ã—ã¦è¿½è¨˜ã€ãªã‘ã‚Œã°æ–°è¦ä½œæˆ"""
    today = data.get("date", date.today().isoformat())

    if data["type"] == "é£Ÿäº‹è¨˜éŒ²":
        existing = find_today_meal_record(today)

        if existing:
            # â”€â”€ æ—¢å­˜ãƒ¬ã‚³ãƒ¼ãƒ‰ã«è¿½è¨˜ãƒ»åˆç®— â”€â”€
            page_id = existing["id"]
            props   = existing["properties"]

            old_content = props.get("é£Ÿäº‹å†…å®¹", {}).get("rich_text", [])
            old_content_str = old_content[0]["text"]["content"] if old_content else ""
            new_content_str = old_content_str + "ï½œ" + data.get("content", "") if old_content_str else data.get("content", "")

            old_kcal    = props.get("ã‚«ãƒ­ãƒªãƒ¼(kcal)",  {}).get("number") or 0
            old_protein = props.get("ã‚¿ãƒ³ãƒ‘ã‚¯è³ª(g)",   {}).get("number") or 0
            old_carbs   = props.get("ç‚­æ°´åŒ–ç‰©(g)",     {}).get("number") or 0
            old_fat     = props.get("è„‚è³ª(g)",         {}).get("number") or 0

            update_body = {
                "properties": {
                    "é£Ÿäº‹å†…å®¹":         {"rich_text": [{"text": {"content": new_content_str}}]},
                    "ã‚«ãƒ­ãƒªãƒ¼(kcal)":   {"number": round(old_kcal    + data.get("kcal", 0),    1)},
                    "ã‚¿ãƒ³ãƒ‘ã‚¯è³ª(g)":    {"number": round(old_protein + data.get("protein", 0), 1)},
                    "ç‚­æ°´åŒ–ç‰©(g)":      {"number": round(old_carbs   + data.get("carbs", 0),   1)},
                    "è„‚è³ª(g)":          {"number": round(old_fat     + data.get("fat", 0),     1)},
                    "ç·´ç¿’æ—¥":           {"checkbox": data.get("is_practice_day", False)},
                    "ãƒ¡ãƒ¢ãƒ»ã‚¢ãƒ‰ãƒã‚¤ã‚¹": {"rich_text": [{"text": {"content": data.get("memo", "")}}]},
                }
            }
            requests.patch(
                f"https://api.notion.com/v1/pages/{page_id}",
                headers=NOTION_HEADERS,
                json=update_body,
            ).raise_for_status()
            return "æ›´æ–°ï¼ˆè¿½è¨˜ï¼‰"

        else:
            # â”€â”€ æ–°è¦ä½œæˆ â”€â”€
            body = {
                "parent": {"database_id": DB["é£Ÿäº‹è¨˜éŒ²"]},
                "properties": {
                    "æ—¥ä»˜":             {"title": [{"text": {"content": today}}]},
                    "é£Ÿäº‹å†…å®¹":         {"rich_text": [{"text": {"content": data.get("content", "")}}]},
                    "ã‚«ãƒ­ãƒªãƒ¼(kcal)":   {"number": data.get("kcal", 0)},
                    "ã‚¿ãƒ³ãƒ‘ã‚¯è³ª(g)":    {"number": data.get("protein", 0)},
                    "ç‚­æ°´åŒ–ç‰©(g)":      {"number": data.get("carbs", 0)},
                    "è„‚è³ª(g)":          {"number": data.get("fat", 0)},
                    "ç·´ç¿’æ—¥":           {"checkbox": data.get("is_practice_day", False)},
                    "ãƒ¡ãƒ¢ãƒ»ã‚¢ãƒ‰ãƒã‚¤ã‚¹": {"rich_text": [{"text": {"content": data.get("memo", "")}}]},
                },
            }
            requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json=body).raise_for_status()
            return "æ–°è¦ä½œæˆ"

    elif data["type"] == "ç·´ç¿’è¨˜éŒ²":
        existing = find_today_practice_record(today)

        if existing:
            page_id = existing["id"]
            props   = existing["properties"]

            old_content = props.get("ç·´ç¿’å†…å®¹", {}).get("rich_text", [])
            old_content_str = old_content[0]["text"]["content"] if old_content else ""
            new_content_str = old_content_str + "ï½œ" + data.get("content", "") if old_content_str else data.get("content", "")

            old_duration = props.get("ç·´ç¿’æ™‚é–“(åˆ†)",      {}).get("number") or 0
            old_kcal     = props.get("æ¶ˆè²»ã‚«ãƒ­ãƒªãƒ¼(kcal)", {}).get("number") or 0

            update_props = {
                "ç·´ç¿’å†…å®¹":           {"rich_text": [{"text": {"content": new_content_str}}]},
                "ç·´ç¿’æ™‚é–“(åˆ†)":       {"number": old_duration + data.get("duration_min", 0)},
                "æ¶ˆè²»ã‚«ãƒ­ãƒªãƒ¼(kcal)": {"number": round(old_kcal + data.get("kcal_burned", 0), 1)},
                "è² è·ãƒ¬ãƒ™ãƒ«":         {"select": {"name": data.get("load_level", "ä¸­")}},
                "ç–²åŠ´åº¦(1-5)":        {"number": data.get("fatigue", 3)},
                "å›žå¾©ã‚¢ãƒ‰ãƒã‚¤ã‚¹":     {"rich_text": [{"text": {"content": data.get("recovery_advice", "")}}]},
            }
            if data.get("video_url"):
                update_props["å‚è€ƒå‹•ç”»URL"] = {"url": data["video_url"]}
            if data.get("video_memo"):
                update_props["å‹•ç”»ãƒ¡ãƒ¢"] = {"rich_text": [{"text": {"content": data["video_memo"]}}]}

            requests.patch(
                f"https://api.notion.com/v1/pages/{page_id}",
                headers=NOTION_HEADERS,
                json={"properties": update_props},
            ).raise_for_status()
            return "æ›´æ–°ï¼ˆè¿½è¨˜ï¼‰"

        else:
            props = {
                "æ—¥ä»˜":               {"title": [{"text": {"content": today}}]},
                "ç·´ç¿’å†…å®¹":           {"rich_text": [{"text": {"content": data.get("content", "")}}]},
                "ç·´ç¿’æ™‚é–“(åˆ†)":       {"number": data.get("duration_min", 0)},
                "æ¶ˆè²»ã‚«ãƒ­ãƒªãƒ¼(kcal)": {"number": data.get("kcal_burned", 0)},
                "è² è·ãƒ¬ãƒ™ãƒ«":         {"select": {"name": data.get("load_level", "ä¸­")}},
                "ç–²åŠ´åº¦(1-5)":        {"number": data.get("fatigue", 3)},
                "å›žå¾©ã‚¢ãƒ‰ãƒã‚¤ã‚¹":     {"rich_text": [{"text": {"content": data.get("recovery_advice", "")}}]},
            }
            if data.get("video_url"):
                props["å‚è€ƒå‹•ç”»URL"] = {"url": data["video_url"]}
            if data.get("video_memo"):
                props["å‹•ç”»ãƒ¡ãƒ¢"] = {"rich_text": [{"text": {"content": data["video_memo"]}}]}

            requests.post(
                "https://api.notion.com/v1/pages",
                headers=NOTION_HEADERS,
                json={"parent": {"database_id": DB["ç·´ç¿’è¨˜éŒ²"]}, "properties": props},
            ).raise_for_status()
            return "æ–°è¦ä½œæˆ"

    elif data["type"] == "ãƒ¬ã‚·ãƒ”":
        body = {
            "parent": {"database_id": DB["ãƒ¬ã‚·ãƒ”å¸³"]},
            "properties": {
                "ãƒ¬ã‚·ãƒ”å":         {"title": [{"text": {"content": data.get("name", "")}}]},
                "ææ–™ãƒ»åˆ†é‡":       {"rich_text": [{"text": {"content": data.get("ingredients", "")}}]},
                "ã‚«ãƒ­ãƒªãƒ¼(kcal)":   {"number": data.get("kcal_per_serving", 0)},
                "ã‚¿ãƒ³ãƒ‘ã‚¯è³ª(g)":    {"number": data.get("protein", 0)},
                "ç‚­æ°´åŒ–ç‰©(g)":      {"number": data.get("carbs", 0)},
                "è„‚è³ª(g)":          {"number": data.get("fat", 0)},
                "ãƒãƒ‰ãƒŸãƒ³ãƒˆãƒ³è©•ä¾¡": {"select": {"name": data.get("rating", "â—‹ è‰¯å¥½")}},
                "ä½œã£ãŸæ—¥":         {"date": {"start": today}},
                "ãƒ¡ãƒ¢":             {"rich_text": [{"text": {"content": data.get("memo", "")}}]},
            },
        }
        requests.post("https://api.notion.com/v1/pages", headers=NOTION_HEADERS, json=body).raise_for_status()
        return "æ–°è¦ä½œæˆ"

    return "ã‚¹ã‚­ãƒƒãƒ—"


# â”€â”€ GitHub Issue ã‚³ãƒ¡ãƒ³ãƒˆ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def post_github_comment(body: str):
    url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}/comments"
    requests.post(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        json={"body": body},
    ).raise_for_status()


# â”€â”€ ãƒ¡ã‚¤ãƒ³ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def main():
    print(f"å…¥åŠ›:\n{ISSUE_BODY}\n")

    # æ—¥ä»˜ã‚’å…¥åŠ›ã‹ã‚‰æŠ½å‡ºï¼ˆãªã‘ã‚Œã°ä»Šæ—¥ï¼‰
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", ISSUE_BODY)
    target_date = date_match.group(1) if date_match else date.today().isoformat()

    # å½“æ—¥ç´¯è¨ˆã‚’Notionã‹ã‚‰å–å¾—
    today_totals = get_today_totals(target_date)
    print(f"å½“æ—¥ç´¯è¨ˆ: {today_totals}\n")

    claude_response = ask_claude(ISSUE_BODY, today_totals, target_date)
    print(f"Claudeå¿œç­”:\n{claude_response}\n")

    notion_data   = extract_json(claude_response)
    notion_status = ""

    if notion_data:
        try:
            action = save_to_notion(notion_data)
            notion_status = f"\n\nâœ… **Notionã«{action}ã—ã¾ã—ãŸ**"
        except Exception as e:
            notion_status = f"\n\nâš ï¸ Notionä¿å­˜ã‚¨ãƒ©ãƒ¼: {e}"
    else:
        notion_status = "\n\nâš ï¸ ãƒ‡ãƒ¼ã‚¿å½¢å¼ã‚’èªè­˜ã§ãã¾ã›ã‚“ã§ã—ãŸã€‚ã‚‚ã†ä¸€åº¦é€ã£ã¦ãã ã•ã„ã€‚"

    post_github_comment(claude_response + notion_status)
    print("å®Œäº†")


if __name__ == "__main__":
    main()
