# Startup Funding Digest — Daily Email Agent

Sends a formatted daily funding digest at **8:00 AM IST** to your inbox.
Powered by Claude (web search) + Gmail SMTP. Runs free on GitHub Actions.

---

## Setup (10 minutes)

### 1. Create a GitHub repo
- Go to github.com → New repository → name it `funding-digest`
- Upload `digest.py` and `.github/workflows/digest.yml` (keep the folder structure)

### 2. Get a Gmail App Password
Gmail requires an App Password (not your regular password) for SMTP access.

1. Go to myaccount.google.com → Security
2. Enable **2-Step Verification** if not already on
3. Search for "App passwords" → Create one → Select "Mail" → Copy the 16-character password

### 3. Add GitHub Secrets
In your repo → Settings → Secrets and variables → Actions → **New repository secret**

Add these 4 secrets:

| Secret name        | Value                                      |
|--------------------|--------------------------------------------|
| `ANTHROPIC_API_KEY`  | Your key from console.anthropic.com        |
| `RECIPIENT_EMAIL`    | Email where you want the digest            |
| `GMAIL_USER`         | Your Gmail address (e.g. you@gmail.com)    |
| `GMAIL_APP_PASSWORD` | The 16-char App Password from step 2       |

### 4. Add GitHub Variables (optional — have defaults)
In Settings → Secrets and variables → Actions → **Variables** tab

| Variable | Default   | Options                                      |
|----------|-----------|----------------------------------------------|
| `REGION` | worldwide | India, USA, Europe, Southeast Asia, worldwide |
| `STAGE`  | any stage | pre-seed and seed, Series A and Series B, etc |
| `SECTOR` | (blank)   | AI, Fintech, SaaS, HealthTech, etc.           |
| `COUNT`  | 8         | 5, 8, 12                                      |

### 5. Enable Actions
- Go to your repo → Actions tab → click "Enable GitHub Actions"
- The workflow runs automatically every day at 8 AM IST
- To test immediately: Actions → "Daily Funding Digest" → "Run workflow"

---

## Schedule
The cron is set to `30 2 * * *` (2:30 AM UTC = 8:00 AM IST).
Edit `.github/workflows/digest.yml` to change the time.

## Cost
- GitHub Actions: **free** (2,000 minutes/month on free tier; this uses ~2 min/day)
- Anthropic API: ~$0.01–0.03 per run (web search + Claude Sonnet)

## Troubleshooting
- **Email not arriving**: Check your Gmail App Password. Make sure 2FA is on.
- **No startups found**: The web search may have returned sparse results. Check Actions logs.
- **Rate limit error**: Your Anthropic API key may have a low limit — check console.anthropic.com.
