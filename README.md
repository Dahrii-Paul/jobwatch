# [JobWatch](https://dahrii-paul.github.io/jobwatch/) 🧬

**An AI job-search agent for bioinformatics, computational biology and genomics.**
It watches Indian recruitment portals (ICMR, DBT/BRIC, DST, CSIR, ICAR/ASRB, UPSC, institutes) for **permanent Scientist and Assistant Professor posts**, and Indian + international sites (SciLifeLab, EURAXESS, jobs.ac.uk, Nature Careers, universities in Sweden, the Netherlands, Switzerland, Germany, Denmark, Austria, Singapore, Australia, UK) for **postdocs and fellowships** — with deadlines.

Runs free on GitHub Actions twice a day, publishes a dashboard on GitHub Pages, and opens a GitHub issue (which GitHub e-mails you) whenever new matches appear.

<!-- STATS:START -->
## Live stats · updated 2026-11-11 01:32

| Metric | Count |
|---|---|
| 🎯 Open matches | **352** |
| 🏛️ Permanent posts — India | **84** |
| 🔬 Postdocs / fellowships — India | **16** |
| ✈️ Postdocs / fellowships — abroad | **158** |
| 🌍 Permanent / faculty — abroad | **35** |
| ⏰ Closing within 14 days | **76** |
| 🆕 New this run | **6** |
| 📡 Sources working | **167 / 209** |

### ⏳ Closing within 30 days

| Left | Position | Type | Where | Deadline |
|---|---|---|---|---|
| 🔴 **0d** | [Research Fellow (Maternity Cover)](https://www.jobs.ac.uk/job/DTM042/research-fellow-maternity-cover) | postdoc | United Kingdom | 2026-11-11 |
| 🔴 **0d** | [Research Fellow (Maternity Cover) London School of Hygiene & Tropical Medicine · United Ki](https://www.openpostdoc.org/position/5bf7ef89-ffd7-450d-a1b3-9cf74da0e7f0) | postdoc | United Kingdom | 2026-11-11 |
| 🔴 **0d** | [Postdoctoral Research Scientist - Epitranscriptomics University of Oxford · Oxford ·](https://www.openpostdoc.org/position/d7c32bfb-dd7c-46be-a870-f665e7429975) | postdoc | United Kingdom | 2026-11-11 |
| 🔴 **0d** | [Post-Doctoral Fellowship in Chemical Escola Superior de Agricultura Luiz de Queiroz (ESALQ](https://www.openpostdoc.org/position/da370722-ee86-44f6-b331-ac1108b5505e) | postdoc | International | 2026-11-11 |
| 🔴 **0d** | [Research Associate Position at IIT Gandhinagar: India](https://researchersjob.com/research-associate-position-at-iit/) | postdoc | India | 2026-11-11 |
| 🔴 **1d** | [Post-doc position on Multi-omics Post-doc Position on Multi-omics in Hereditary Fibrinogen](https://www.academictransfer.com/en/jobs/364732/post-doc-position-on-multi-omics/) | postdoc | Netherlands | 2026-11-12 |
| 🔴 **1d** | [Post-doctoral Fellow in Bioinformatics in the Hong Kong Jockey Club Global Health Institut](https://www.timeshighereducation.com/unijobs/listing/414711/post-doctoral-fellow-in-bioinformatics-in-the-hong-kong-jockey-club-global-health-institute/?LinkSource=PremiumListing) | postdoc | Hong Kong | 2026-11-12 |
| 🔴 **1d** | [Assistant Project Scientist - IGI’s Entrepreneurial Fellows Program - Innovative Genomics ](https://www.openpostdoc.org/position/1333ed87-a95c-4aa4-974d-664e0759cd2b) | project | International | 2026-11-12 |
| 🔴 **1d** | [Post-doctoral Fellow in Bioinformatics in the Hong Kong Jockey Club Global Health Institut](https://www.openpostdoc.org/position/1ab0de62-4c61-4b3c-b2fb-f7f92c25f5e1) | postdoc | Hong Kong | 2026-11-12 |
| 🔴 **1d** | [Research Associate/ Senior Research Associate in AI-Enabled Enzyme Engineering for PET Bio](https://www.jobs.ac.uk/job/DTL498/research-associate-senior-research-associate-in-ai-enabled-enzyme-engineering-for-pet-biorecycling) | postdoc | United Kingdom | 2026-11-12 |
| 🔴 **1d** | [Research Associate - Locke Group (Fixed Term) University of Cambridge · United Kingdom ·](https://www.openpostdoc.org/position/09e12ae9-7edf-4d5b-bb1d-a1a90870177e) | postdoc | United Kingdom | 2026-11-12 |
| 🔴 **1d** | [Research Associate/ Senior Research Associate in AI-Enabled Enzyme Engineering for PET Bio](https://www.openpostdoc.org/position/d42bd020-48ea-4c8d-bbac-084125334f80) | postdoc | United Kingdom | 2026-11-12 |
| 🔴 **1d** | [Official Faculty Recruitment Advertisement (PDF)](https://careers.iith.ac.in/documents/IITH_Faculty_Recruitment_Advt-Oct_2026-final.pdf) | permanent | India | 2026-11-12 |
| 🔴 **2d** | [(Senior) Postdoctoral Research Scientist](https://www.jobs.ac.uk/job/DTE706/senior-postdoctoral-research-scientist) | postdoc | United Kingdom | 2026-11-13 |
| 🔴 **2d** | [Post-doctoral Research Fellow - AR3357 University of St Andrews · United Kingdom ·](https://www.openpostdoc.org/position/141759d8-9559-45a6-b46b-dc534416d588) | postdoc | United Kingdom | 2026-11-13 |
<!-- STATS:END -->

---

## How it works

```
config/sources.yaml ──► 1. Collect   listing pages, RSS and WordPress APIs (50 sites, in parallel)
                        2. Read      opens each promising advert page / PDF to find the deadline and subjects
config/profile.yaml ──► 3. Score     keyword rules: category, India/abroad, relevance 0–100
                        4. Screen    AI reads the advert against your profile (free GitHub Models)
                        5. Publish   data/*.json, Atom feed, README stats, dashboard (index.html)
                        6. Alert     GitHub issue + optional Telegram for new matches
config/programs.yaml ─► fellowship schemes (EMBO, MSCA, HFSP, Humboldt, N-PDF, DBT-RA …) checked each run
```

| Category | What it catches |
|---|---|
| **Permanent / faculty** | Scientist B/C/D…, Scientist-I…V (BRIC), Assistant/Associate Professor, lecturer, staff scientist, group leader |
| **Postdoc** | Postdoc, Research Associate (RA-I/II/III), Research Fellow |
| **Fellowship** | Named schemes — Ramalingaswami, INSPIRE Faculty, India Alliance, EMBO, MSCA… |
| Project / PhD | JRF, SRF, project scientist, PhD — collected but hidden by default |

For government adverts like *"30 vacancies of Scientist-B at ICMR"* the subject is only in the PDF, so the agent opens the PDF and looks for bioinformatics / genomics; if it can't tell, the post is flagged *"check the advert"* rather than dropped.

---

## Set up on GitHub (10 minutes, all free)

1. **Create the repo.** On GitHub: *New repository* → name it `jobwatch` → **Public** (Pages and Actions minutes are free for public repos) → create. Then upload these files (drag the unzipped folder contents into *Add file → Upload files*, or use git):
   ```bash
   cd jobwatch
   git init && git add . && git commit -m "JobWatch"
   git branch -M main
   git remote add origin https://github.com/<you>/jobwatch.git
   git push -u origin main
   ```
2. **Allow the workflow to save results.** *Settings → Actions → General → Workflow permissions* → **Read and write permissions** → Save.
3. **Turn on the website.** *Settings → Pages* → Source **Deploy from a branch** → Branch **main**, folder **/ (root)** → Save. Your dashboard will be at `https://<you>.github.io/jobwatch/`.
4. **Run it once.** *Actions → Scan for jobs → Run workflow*. Takes ~10–20 min. After that it runs every day at 08:17 and 18:17 IST.
5. **Get e-mails.** Click **Watch → All activity** on your repo. Each new-jobs issue then arrives in your inbox.
6. **Check the Sources tab** on the dashboard (or `data/health.json`). Fix or disable any source that shows *Needs a look* — see below.

### Optional extras

| Want | Do this |
|---|---|
| Telegram alerts | Create a bot with @BotFather, get your chat id, add repo secrets `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` |
| AI screening keeps failing (403) | Create a fine-grained token with only **Models: read** at github.com/settings/tokens and save it as secret `MODEL_TOKEN` |
| Use Gemini / OpenAI / Groq instead | Secret `LLM_API_KEY`; repo *variables* `LLM_BASE_URL` (e.g. `https://generativelanguage.googleapis.com/v1beta/openai`) and `LLM_MODEL` (e.g. `gemini-2.0-flash`) |
| No AI at all | Nothing to do if no key works — keyword scoring still runs. Or add variable `AI_DISABLED=true` |
| Change schedule | Edit the two `cron:` lines in `.github/workflows/scan.yml` (times are UTC) |

---

## Save a job you found yourself (LinkedIn, X, ResearchGate…)

LinkedIn, X and ResearchGate block automated reading, so JobWatch doesn't scan them. Instead, when you spot a post there:

1. Paste its link into **"Found a job on LinkedIn, X, ResearchGate or anywhere else?"** on the dashboard and press **Save job** (or open *Issues → New issue → Save a job*).
2. Fill in the job title (and the deadline if you know it) and submit.
3. About two minutes later the job is on your dashboard and in the feed, tagged **Saved by you**, with a deadline countdown and a match score. JobWatch replies on the issue and closes it.

For normal websites (university pages, PDFs) the agent reads the title and deadline itself. Edit the issue to change a saved job. Only you, the repo owner, can add jobs.

---

## LinkedIn job alerts → your dashboard (automatic)

LinkedIn has no public jobs API and forbids scraping, but it will e-mail you new jobs for saved searches. A small script in your Gmail forwards those alert e-mails' jobs to JobWatch every hour. Jobs that match your profile appear on the dashboard tagged **LinkedIn alert**; LinkedIn gives no deadline, so they drop off 30 days after they arrive.

**1. Turn on LinkedIn job alerts** (signed in to LinkedIn with the Gmail address you'll use)
Search LinkedIn Jobs for e.g. *postdoctoral bioinformatics* (India), *computational biology postdoc* (Europe), *scientist genomics* (India), and switch on **Job alert** for each search. Choose *Daily* and *Email*.

**2. Create a GitHub token** (lets the script add jobs to this repo, nothing else)
github.com → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → *Generate new token*
- Expiration: 1 year · Repository access: **Only select repositories → jobwatch**
- Permissions → Repository permissions → **Contents: Read and write** (leave everything else as is)
- Generate and copy the token (starts with `github_pat_`).

**3. Install the Gmail script**
- Go to https://script.google.com (signed in to that Gmail) → **New project**.
- Delete the sample code, paste the whole of [`tools/gmail-linkedin-alerts.gs`](tools/gmail-linkedin-alerts.gs), click 💾 Save.
- ⚙️ **Project Settings** → *Script properties* → **Add script property**: `GITHUB_TOKEN` = the token → Save.
- Back in the editor, choose **testWithoutSending** in the function menu → **Run**. Google asks you to authorise the script (it needs to read Gmail): *Review permissions → your account → Advanced → Go to project → Allow*. The log lists the jobs found in your recent alert e-mails.
- Choose **installHourlyCheck** → **Run**. Done — it now checks every hour.

**Saving posts from X, ResearchGate, WhatsApp… by e-mail.** The same Gmail script also picks up e-mails you send *to yourself* with **jobwatch** in the subject. On your phone: open the post → **Share → Gmail** → send to your own address with the subject `jobwatch: <job title>` (e.g. `jobwatch: Postdoc in TB genomics, NCBS — apply by 30 Nov 2026`). Within an hour it is on your dashboard tagged *Saved by you*; a deadline written in the subject is picked up automatically.

To stop it: in script.google.com open the project → ⏰ Triggers → delete the trigger.

---

## Make it yours

- **`config/profile.yaml`** — your summary (the AI reads this), keywords, things to exclude, match threshold, countries of interest.
- **`config/sources.yaml`** — add a site in 5 lines:
  ```yaml
  - id: nipgr
    name: NIPGR New Delhi
    region: india
    urls: ["https://www.nipgr.ac.in/careers"]
    life_science: true
  ```
  Use `link_pattern` to keep only links whose URL contains e.g. `/job/`, `render: true` for sites that only load with JavaScript, `type: rss` for feeds.
- **`config/programs.yaml`** — recurring fellowship schemes.

### About the LinkedIn short links

`lnkd.in/…` links can't be followed by a bot (LinkedIn blocks them), so the institutions from that list are included through their own career pages instead.

### Sources marked `verified: false`

The ICMR, DBT, SciLifeLab and Researchersjob pages were checked while building this. Others are the institutions' known career pages but sites move often: the first run's **Sources** tab tells you which ones return nothing. Each source lists fallback URLs (usually the homepage, whose "Recruitment / What's new" links the agent also understands).

---

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m jobwatch.run --no-ai --no-notify            # everything
python -m jobwatch.run --only icmr scilifelab -v      # a few sources, verbose
python -m http.server 8080                            # dashboard at http://localhost:8080
python -m pytest -q                                   # tests (no network needed)
```

## Data endpoints (served by GitHub Pages)

```
data/jobs.json      everything indexed (open, closed, weaker matches)
data/open.json      open matches only
data/urgent.json    open matches closing within 14 days
data/programs.json  fellowship schemes and their current call dates
data/health.json    per-source status from the last run
data/feed.xml       Atom feed — subscribe in any RSS reader
```

---

*Always confirm eligibility, age limits, reservation and the deadline in the official advertisement. Data is gathered from public pages for personal, non-commercial use; the agent fetches politely (one request per second per site, twice a day).*
