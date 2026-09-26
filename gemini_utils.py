"""
gemini_utils.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env with EXPLICIT path so it always works
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)

import json
import re
from typing import Optional, Dict, Any, List

# --- New SDK import ---
try:
    from google import genai
    from google.genai import types
    from PIL import Image
    GENAI_AVAILABLE = True
except Exception as e:
    print(f"[PocketSmart] google-genai import failed: {e}")
    GENAI_AVAILABLE = False


# ------------------------------------------------------------------
# Gemini client bootstrap
# ------------------------------------------------------------------
_client = None
# Models to try in order — the first that works gets cached
MODEL_CANDIDATES = [
    "gemini-3.6-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-flash-latest",
]
MODEL_NAME = MODEL_CANDIDATES[0]  # will be auto-updated after first success
_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if GENAI_AVAILABLE and _api_key:
    try:
        _client = genai.Client(api_key=_api_key)
        print("[PocketSmart] Gemini SDK online - finding working model...")
        _found = False
        for _candidate in MODEL_CANDIDATES:
            try:
                _test = _client.models.generate_content(
                    model=_candidate,
                    contents="Reply with exactly: OK"
                )
                print(f"[PocketSmart] Working model: {_candidate}")
                print(f"[PocketSmart] Test reply: {_test.text.strip()[:40]}")
                print("[PocketSmart] Gemini AI online")
                MODEL_NAME = _candidate
                _found = True
                break
            except Exception as _e:
                msg = str(_e)[:80]
                print(f"[PocketSmart]   {_candidate} -> {msg}")
        if not _found:
            print("[PocketSmart] No working model found. OFFLINE DEMO MODE")
            _client = None
    except Exception as e:
        print(f"[PocketSmart] Gemini init failed: {e}")
        print("[PocketSmart] Falling back to OFFLINE DEMO MODE")
        _client = None
else:
    if not _api_key:
        print("[PocketSmart] No GEMINI key -> running OFFLINE DEMO MODE")
    else:
        print("[PocketSmart] SDK unavailable -> running OFFLINE DEMO MODE")


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        s = text.find("{"); e = text.rfind("}")
        if s != -1 and e != -1 and e > s:
            try: return json.loads(text[s:e+1])
            except Exception: pass
    return {}


def _shopping_links(term: str, platforms: List[str]) -> Dict[str, str]:
    if not term: return {}
    q = term.replace(" ", "+")
    urls = {
        "Amazon":     f"https://www.amazon.in/s?k={q}",
        "Flipkart":   f"https://www.flipkart.com/search?q={q}",
        "IKEA":       f"https://www.ikea.com/in/en/search/?q={q}",
        "Swiggy":     f"https://www.swiggy.com/search?query={q}",
        "Zomato":     f"https://www.zomato.com/search?q={q}",
        "OYO":        f"https://www.oyorooms.com/search/?location={q}",
        "BookMyShow": f"https://in.bookmyshow.com/explore/events?q={q}",
        "Bluestone":  f"https://www.bluestone.com/search.html?query={q}",
        "Tanishq":    f"https://www.tanishq.co.in/search?q={q}",
        "CaratLane":  f"https://www.caratlane.com/search?q={q}",
        "Melorra":    f"https://www.melorra.com/search?q={q}",
        "Myntra":     f"https://www.myntra.com/search?q={q}",
    }
    return {k: v for k, v in urls.items() if k in platforms}


# ------------------------------------------------------------------
# Fallback generators (used when Gemini is offline)
# ------------------------------------------------------------------
def _fallback_home(inp) -> Dict[str, Any]:
    total = float(inp.total_budget)
    split = {"Lighting": 0.20, "Fans": 0.20, "Furniture": 0.40, "Dining": 0.20}
    qty_map = {
        "Lighting":  inp.num_lights,
        "Fans":      inp.num_fans,
        "Furniture": inp.num_furniture,
        "Dining":    inp.num_dining_tables,
    }
    breakdown = []
    for cat, pct in split.items():
        qty = qty_map[cat]
        if qty <= 0: continue
        alloc = round(total * pct, 2)
        unit = round(alloc / qty, 2)
        breakdown.append({
            "category": cat,
            "allocation": alloc,
            "items": [{
                "name": f"Smart {cat} (x{qty})",
                "description": f"Budget-friendly {cat.lower()} for {inp.room_type or 'room'}",
                "estimated_price": unit,
                "quantity": qty,
                "search_terms": f"{cat.lower()} {inp.room_type or ''}".strip(),
                "platforms": ["Amazon", "Flipkart", "IKEA"],
            }]
        })
    spent = sum(c["allocation"] for c in breakdown)
    return {
        "total_budget": total, "currency": "INR",
        "budget_breakdown": breakdown,
        "remaining_budget": round(total - spent, 2),
        "styling_tips": [
            "Layer ambient + task lighting for depth.",
            "Prefer neutral base tones with one accent color.",
            "Keep walkways clear for a spacious feel.",
        ],
    }


def _fallback_party(inp) -> Dict[str, Any]:
    total = float(inp.total_budget)
    guests = max(inp.num_guests, 1)
    split = {"Venue": 0.30, "Catering": 0.40, "Decoration": 0.15, "Entertainment": 0.15}
    breakdown = []
    for cat, pct in split.items():
        alloc = round(total * pct, 2)
        breakdown.append({
            "category": cat, "allocation": alloc,
            "items": [{
                "name": f"{cat} package for {guests} guests",
                "description": f"Curated {cat.lower()} for a {inp.party_type}",
                "estimated_price": alloc, "quantity": 1,
                "search_terms": f"{inp.party_type} {cat.lower()} {guests} guests",
                "platforms": ["Swiggy", "Zomato", "OYO", "BookMyShow"],
            }]
        })
    spent = sum(c["allocation"] for c in breakdown)
    return {
        "total_budget": total, "currency": "INR",
        "budget_breakdown": breakdown,
        "venue_suggestions": [{
            "name": "Local Banquet Hall",
            "type": inp.venue_type or "Indoor",
            "capacity": guests,
            "estimated_cost": breakdown[0]["allocation"],
            "search_terms": f"banquet hall near me for {guests}",
        }],
        "remaining_budget": round(total - spent, 2),
        "additional_suggestions": [
            "Book vendors 2-3 weeks in advance.",
            "Negotiate buffet packages for 10% savings.",
            "Add a photo booth for guest engagement.",
        ],
    }


def _fallback_jewelry(inp, has_image: bool) -> Dict[str, Any]:
    total = float(inp.total_budget)
    occ = (inp.occasion or "General").lower()
    split = [("Necklace", 0.45), ("Earrings", 0.25), ("Bracelet", 0.20), ("Ring", 0.10)]
    items = []
    for name, pct in split:
        items.append({
            "item_type": name,
            "description": f"{name} styled for {occ}",
            "style": "Elegant / Modern",
            "estimated_price": round(total * pct, 2),
            "search_terms": f"{name.lower()} for {occ}",
            "platforms": ["Amazon", "Flipkart", "Bluestone", "Tanishq", "CaratLane", "Myntra"],
        })
    spent = sum(i["estimated_price"] for i in items)
    tips = [
        "Match metal tone with your outfit hardware.",
        "For day events go lighter; evenings go bolder.",
        "Upload an outfit image for sharper matching.",
    ]
    if has_image: tips.append("Image received - matched to outfit colors.")
    return {
        "total_budget": total, "currency": "INR",
        "jewelry_recommendations": items,
        "remaining_budget": round(total - spent, 2),
        "styling_tips": tips,
    }


# ------------------------------------------------------------------
# Public API — uses new google-genai SDK when available
# ------------------------------------------------------------------
def get_home_recommendations(inp) -> Dict[str, Any]:
    if _client is None:
        data = _fallback_home(inp)
    else:
        prompt = f"""You are PocketSmart AI, expert Indian home interior budget planner.
Budget INR {inp.total_budget}. Room: {inp.room_type}.
Lights: {inp.num_lights}, Fans: {inp.num_fans}, Furniture: {inp.num_furniture}, Dining tables: {inp.num_dining_tables}.
Return ONLY valid JSON exactly:
{{"total_budget":{inp.total_budget},"currency":"INR","budget_breakdown":[{{"category":"Lighting","allocation":0.0,"items":[{{"name":"","description":"","estimated_price":0.0,"quantity":0,"search_terms":"","platforms":["Amazon","Flipkart","IKEA"]}}]}}],"remaining_budget":0.0,"styling_tips":[""]}}
Categories: Lighting, Fans, Furniture, Dining. Sum allocations <= {inp.total_budget}."""
        try:
            r = _client.models.generate_content(model=MODEL_NAME, contents=prompt)
            data = _extract_json(r.text)
            if not data or "budget_breakdown" not in data: raise ValueError("bad response")
            data.setdefault("currency", "INR")
            data.setdefault("styling_tips", [])
            data.setdefault("remaining_budget", 0.0)
            print("[Gemini] home OK")
        except Exception as e:
            print(f"[Gemini] home fallback: {e}")
            data = _fallback_home(inp)
    for c in data.get("budget_breakdown", []):
        for it in c.get("items", []):
            it["shopping_links"] = _shopping_links(
                it.get("search_terms", ""),
                it.get("platforms", ["Amazon", "Flipkart", "IKEA"]))
    return data


def get_party_recommendations(inp) -> Dict[str, Any]:
    if _client is None:
        data = _fallback_party(inp)
    else:
        prompt = f"""You are PocketSmart AI, expert Indian party planner.
Plan a {inp.party_type} for {inp.num_guests} guests within INR {inp.total_budget}.
Venue: {inp.venue_type or 'Flexible'}.
Return ONLY valid JSON exactly:
{{"total_budget":{inp.total_budget},"currency":"INR","budget_breakdown":[{{"category":"Venue","allocation":0.0,"items":[{{"name":"","description":"","estimated_price":0.0,"quantity":1,"search_terms":"","platforms":["Swiggy","Zomato","OYO","BookMyShow"]}}]}}],"venue_suggestions":[{{"name":"","type":"","capacity":0,"estimated_cost":0.0,"search_terms":""}}],"remaining_budget":0.0,"additional_suggestions":[""]}}
Categories: Venue, Catering, Decoration, Entertainment."""
        try:
            r = _client.models.generate_content(model=MODEL_NAME, contents=prompt)
            data = _extract_json(r.text)
            if not data or "budget_breakdown" not in data: raise ValueError("bad")
            data.setdefault("currency", "INR")
            data.setdefault("additional_suggestions", [])
            print("[Gemini] party OK")
        except Exception as e:
            print(f"[Gemini] party fallback: {e}")
            data = _fallback_party(inp)
    for c in data.get("budget_breakdown", []):
        for it in c.get("items", []):
            it["shopping_links"] = _shopping_links(
                it.get("search_terms", ""),
                it.get("platforms", ["Swiggy", "Zomato", "OYO"]))
    for v in data.get("venue_suggestions", []):
        v["shopping_links"] = _shopping_links(v.get("search_terms", ""), ["OYO", "BookMyShow"])
    return data


def get_jewelry_recommendations(inp, image_path: Optional[str] = None) -> Dict[str, Any]:
    has_image = bool(image_path and os.path.exists(image_path))
    if _client is None:
        data = _fallback_jewelry(inp, has_image)
    else:
        base = f"""You are PocketSmart AI, expert Indian jewelry stylist.
Occasion: {inp.occasion}. Budget INR {inp.total_budget}. Preferences: {inp.preferences or 'None'}.
{"Outfit image attached. Analyze colors and style." if has_image else ""}
Return ONLY valid JSON exactly:
{{"total_budget":{inp.total_budget},"currency":"INR","jewelry_recommendations":[{{"item_type":"","description":"","style":"","estimated_price":0.0,"search_terms":"","platforms":["Amazon","Flipkart","Bluestone","Tanishq","CaratLane","Myntra"]}}],"remaining_budget":0.0,"styling_tips":[""]}}"""
        try:
            if has_image:
                img = Image.open(image_path)
                r = _client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[base, img]
                )
            else:
                r = _client.models.generate_content(model=MODEL_NAME, contents=base)
            data = _extract_json(r.text)
            if not data or "jewelry_recommendations" not in data: raise ValueError("bad")
            data.setdefault("currency", "INR")
            data.setdefault("styling_tips", [])
            print("[Gemini] jewelry OK")
        except Exception as e:
            print(f"[Gemini] jewelry fallback: {e}")
            data = _fallback_jewelry(inp, has_image)
    for it in data.get("jewelry_recommendations", []):
        it["shopping_links"] = _shopping_links(
            it.get("search_terms", ""),
            it.get("platforms", ["Amazon", "Flipkart", "Bluestone", "Tanishq", "CaratLane", "Myntra"]))
    return data
