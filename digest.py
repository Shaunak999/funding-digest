import os
import json
import smtplib
from openai import OpenAI
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Config ────────────────────────────────────────────────────────────────────
GROQ_API_KEY        = os.environ["GROQ_API_KEY"]
RECIPIENT_EMAIL     = os.environ["RECIPIENT_EMAIL"]
GMAIL_USER          = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD  = os.environ["GMAIL_APP_PASSWORD"]

REGION  = os.environ.get("REGION", "worldwide")
STAGE   = os.environ.get("STAGE", "any stage")
SECTOR  = os.environ.get("SECTOR", "")
COUNT   = int(os.environ.get("COUNT", "8") or "8")
# ─────────────────────────────────────────────────────────────────────────────

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

def fetch_funding_news() -> list[dict]:
    today = datetime.now().strftime("%B %d, %Y")

    sector_line = f" specifically in the {SECTOR} sector" if SECTOR else ""

    region_line = (
        "worldwide (India, USA, Europe, Southeast Asia)"
        if REGION == "worldwide"
        else f"in {REGION}"
    )

    prompt = f"""
Search the web for the latest {COUNT} tech startup funding news {region_line}
at {STAGE}{sector_line}. Today is {today}.

For each startup, gather:
1. Startup name
2. What they do (2 sentences max, plain language)
3. Names of investors who participated
4. Amount raised and funding stage
5. LinkedIn profile URLs of the top 2-3 people (CEO / CTO / Co-founder)

Respond ONLY with a valid JSON array — no markdown, no backticks, no preamble.

Schema:
[
  {{
    "name": "Startup Name",
    "description": "What they do.",
    "investors": "Sequoia, Accel",
    "amount": "$12M",
    "stage": "Series A",
    "country": "India",
    "linkedins": [
      {{"name": "Alice Roy (CEO)", "url": "https://linkedin.com/in/aliceroy"}},
      {{"name": "Bob Singh (CTO)", "url": "https://linkedin.com/in/bobsingh"}}
    ]
  }}
]

Only output valid JSON.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        text = response.choices[0].message.content.strip()

        clean = (
            text.removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
        )

        start = clean.find("[")
        end = clean.rfind("]")

        if start == -1 or end == -1:
            raise ValueError(f"No JSON array found:\n{text[:500]}")

        return json.loads(clean[start:end + 1])

    except Exception as e:
        print(f"Error fetching funding news: {e}")
        return []


def build_html(startups: list[dict]) -> str:
    today_label = datetime.now().strftime("%A, %B %d, %Y")
    region_label = "Worldwide" if REGION == "worldwide" else REGION

    cards = ""

    for i, s in enumerate(startups, 1):
        linkedin_links = ""

        for l in s.get("linkedins", []):
            linkedin_links += (
                f'<a href="{l["url"]}" '
                f'style="color:#0077b5;text-decoration:none;display:block;'
                f'margin-bottom:4px;font-size:13px;">'
                f'&#x1F517; {l["name"]}</a>'
            )

        cards += f"""
        <tr>
          <td style="padding:22px 0;border-bottom:1px solid #ebebeb;">
            <table width="100%" cellpadding="0" cellspacing="0">

              <tr>
                <td>
                  <span style="background:#ecfdf5;color:#065f46;
                               font-size:11px;font-weight:700;
                               padding:3px 10px;border-radius:4px;
                               letter-spacing:.06em;">
                    #{i} &nbsp;{s.get('stage','FUNDING').upper()}
                  </span>

                  {"&nbsp;<span style='font-size:12px;color:#999;'>"+s['country']+"</span>"
                    if s.get('country') else ""}
                </td>

                <td align="right"
                    style="font-size:20px;font-weight:700;color:#059669;">
                  {s.get('amount','')}
                </td>
              </tr>

              <tr>
                <td colspan="2" style="padding-top:10px;">

                  <div style="font-size:21px;font-weight:700;
                              color:#111;margin-bottom:6px;">
                    {s.get('name','')}
                  </div>

                  <div style="font-size:14px;color:#555;
                              line-height:1.65;margin-bottom:14px;">
                    {s.get('description','')}
                  </div>

                  <table cellpadding="0" cellspacing="0" width="100%">
                    <tr>

                      <td style="vertical-align:top;
                                 padding-right:24px;width:50%;">

                        <div style="font-size:11px;color:#999;
                                    font-weight:700;letter-spacing:.07em;
                                    margin-bottom:5px;">
                          INVESTORS
                        </div>

                        <div style="font-size:13px;color:#333;">
                          {s.get('investors','Undisclosed')}
                        </div>

                      </td>

                      <td style="vertical-align:top;width:50%;">

                        <div style="font-size:11px;color:#999;
                                    font-weight:700;
                                    letter-spacing:.07em;
                                    margin-bottom:5px;">
                          KEY PEOPLE
                        </div>

                        {linkedin_links or '<span style="font-size:13px;color:#aaa;">—</span>'}

                      </td>

                    </tr>
                  </table>

                </td>
              </tr>

            </table>
          </td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f4f4f0;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#f4f4f0;padding:32px 16px;">

<tr>
<td align="center">

<table width="620" cellpadding="0" cellspacing="0"
       style="background:#fff;border-radius:14px;
              overflow:hidden;
              box-shadow:0 1px 4px rgba(0,0,0,.07);">

<tr>
<td style="background:#0f0f0f;padding:30px 36px;">

<div style="font-size:11px;color:#666;
            letter-spacing:.14em;
            font-weight:700;margin-bottom:7px;">
DAILY FUNDING DIGEST
</div>

<div style="font-size:28px;font-weight:800;color:#fff;
            margin-bottom:5px;">
Startup Funding Report
</div>

<div style="font-size:13px;color:#888;">
{today_label} · {region_label}
{' · ' + SECTOR if SECTOR else ''}
</div>

</td>
</tr>

<tr>
<td style="padding:0 36px;">
<table width="100%" cellpadding="0" cellspacing="0">
{cards}
</table>
</td>
</tr>

</table>

</td>
</tr>

</table>

</body>
</html>
"""


def send_email(html: str, startup_count: int):
    today_label = datetime.now().strftime("%b %d, %Y")

    subject = f"Startup Funding Digest — {today_label} ({startup_count} deals)"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = RECIPIENT_EMAIL

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(
            GMAIL_USER,
            RECIPIENT_EMAIL,
            msg.as_string()
        )

    print(f"✓ Sent digest ({startup_count} startups)")


if __name__ == "__main__":
    print("Fetching funding news...")

    startups = fetch_funding_news()

    if not startups:
        print("No startup data found.")
        exit(1)

    print(f"Found {len(startups)} startups.")

    html = build_html(startups)

    print("Sending email...")

    send_email(html, len(startups))