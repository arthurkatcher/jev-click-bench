"""Minimal Jev client: OpenRouter decisions endpoint, images + box (Jev 1.14)."""
import base64, io, json, math, os, pathlib, time
import requests

ROOT = pathlib.Path(__file__).parent
for line in (ROOT / ".env").read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

URL = "https://openrouter.ai/api/alpha/decisions"
MODEL = os.environ.get("JEV_MODEL", "typesafe/jev-1.14")

# Jev image limits (docs.typesafe.ai/images.md): each side 280..1568 px, PNG/JPEG, 16 MiB.
MAX_SIDE, MIN_SIDE = 1568, 280

RETRY_STATUS = {429, 500, 502, 503, 504, 524, 529}
FATAL_STATUS = {401, 402, 403}  # bad key / out of credit: stop the whole run, don't burn through cases


class JevError(Exception):
    def __init__(self, msg, status=None, body=None, attempts=0):
        super().__init__(msg)
        self.status, self.body, self.attempts = status, body, attempts

    @property
    def fatal(self):
        return self.status in FATAL_STATUS


def fit(img):
    """Scale so both sides fit 280..1568 without padding. Box fractions then map 1:1 to the original."""
    w, h = img.size
    s = min(1.0, MAX_SIDE / max(w, h))
    s = max(s, MIN_SIDE / min(w, h))  # tiny images get upscaled
    if s != 1.0:
        img = img.resize((round(w * s), round(h * s)), resample=3)  # 3 = BICUBIC
    return img, s


def data_url(img):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def decide(state, questions, retries=4):
    """state: list of OpenRouter parts ({type:text}|{type:image_url}).
    Returns (json, seconds_of_last_attempt, attempts). Raises JevError (never leaks the key)."""
    body = json.dumps({"model": MODEL, "state": state, "questions": questions})
    headers = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
               "TypeSafe-Danger-Zone-Images": "true", "Content-Type": "application/json"}
    last = None
    for attempt in range(1, retries + 2):
        t = time.time()
        try:
            r = requests.post(URL, headers=headers, data=body, timeout=120)
        except requests.RequestException as e:  # timeouts, connection resets, chunked-encoding errors...
            last = JevError(f"{type(e).__name__}: {e}", attempts=attempt)
            if attempt <= retries:
                time.sleep(2 ** attempt)
            continue
        dt = time.time() - t
        if r.status_code == 200:
            try:
                return r.json(), dt, attempt
            except ValueError:
                raise JevError("200 with a non-JSON body", 200, r.text[:2000], attempt)
        last = JevError(f"HTTP {r.status_code}", r.status_code, r.text[:2000], attempt)
        if r.status_code in RETRY_STATUS:
            try:
                wait = float(r.headers.get("Retry-After"))
                if not math.isfinite(wait):
                    raise ValueError
            except (TypeError, ValueError):
                wait = 2 ** attempt
            if attempt <= retries:
                time.sleep(max(0.0, min(wait, 60.0)))
            continue
        raise last
    raise last


def balance():
    """Remaining credit on the OpenRouter key (float), or an error string. Read-only, free."""
    try:
        r = requests.get("https://openrouter.ai/api/v1/key", timeout=20,
                         headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
        v = r.json()["data"].get("limit_remaining")
        return float(v) if v is not None else "no limit set"
    except Exception as e:
        return f"unavailable ({type(e).__name__})"
