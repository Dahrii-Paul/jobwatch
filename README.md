# [JobWatch](https://dahrii-paul.github.io/jobwatch/) 🧬

**An AI job-search agent for bioinformatics, computational biology and genomics.**
It watches Indian recruitment portals (ICMR, DBT/BRIC, DST, CSIR, ICAR/ASRB, UPSC, institutes) for **permanent Scientist and Assistant Professor posts**, and Indian + international sites (SciLifeLab, EURAXESS, jobs.ac.uk, Nature Careers, universities in Sweden, the Netherlands, Switzerland, Germany, Denmark, Austria, Singapore, Australia, UK) for **postdocs and fellowships** — with deadlines.

Runs free on GitHub Actions twice a day, publishes a dashboard on GitHub Pages, and opens a GitHub issue (which GitHub e-mails you) whenever new matches appear.

<!-- STATS:START -->
## Live stats · updated 2026-11-14 14:55

| Metric | Count |
|---|---|
| 🎯 Open matches | **370** |
| 🏛️ Permanent posts — India | **85** |
| 🔬 Postdocs / fellowships — India | **15** |
| ✈️ Postdocs / fellowships — abroad | **172** |
| 🌍 Permanent / faculty — abroad | **36** |
| ⏰ Closing within 14 days | **78** |
| 🆕 New this run | **4** |
| 📡 Sources working | **166 / 209** |

### ⏳ Closing within 30 days

| Left | Position | Type | Where | Deadline |
|---|---|---|---|---|
| 🔴 **0d** | [Faculty of Health Sciences - Precision Medicine and Health Tech](https://www.timeshighereducation.com/unijobs/listing/403495/faculty-of-health-sciences-precision-medicine-and-health-tech/?LinkSource=PremiumListing) | permanent | International | 2026-11-14 |
| 🔴 **0d** | [Postdoctoral Scholar - Bioinformatician for Tree Improvement University of Alberta · Edmon](https://www.openpostdoc.org/position/c80202f0-6fac-452f-9a9b-aac6fa284be7) | postdoc | International | 2026-11-14 |
| 🔴 **0d** | [LVPEI Hyderabad Project Research Scientist-I (Non-Medical) — Ocular Oncology / ICMR Biomar](https://www.biotecnika.org/2026/11/lvpei-project-research-scientist-hyderabad-2026/) | project | India | 2026-11-14 |
| 🔴 **1d** | [Project Fellow / Research Fellow (DHR TRANS-MAP Peripheral Nerve Transcriptomics) at Presi](https://www.biotecnika.org/2026/11/presidency-university-project-fellow-dhr-trans-map/) | project | India | 2026-11-15 |
| 🔴 **1d** | [Postdoctoral Researcher: Reset Aged Vascular Function Welcome to Maastricht University! Wh](https://www.academictransfer.com/en/jobs/364997/postdoctoral-researcher-reset-aged-vascular-function/) | postdoc | Netherlands | 2026-11-15 |
| 🔴 **1d** | [Postdoctoral Position in Multi-Omics Machine Learning and Computational Cancer Biology at ](https://researchersjob.com/postdoctoral-position-in-multi-omics-machine-learning-2/) | postdoc | Sweden | 2026-11-15 |
| 🔴 **1d** | [Postdoc in Multi-omics Machine Learning and Computational Cancer Biology at KTH Royal Inst](https://researchersjob.com/postdoc-in-multi-omics-machine-learning-2/) | postdoc | Sweden | 2026-11-15 |
| 🔴 **1d** | [Postdoc in Multi-Omics Machine Learning and Computational Cancer Biology at KTH Royal Inst](https://researchersjob.com/postdoc-in-multi-omics-machine-learning/) | postdoc | Sweden | 2026-11-15 |
| 🔴 **1d** | [Postdoctoral Position in Multi-Omics Machine Learning and Computational Cancer Biology, Sw](https://researchersjob.com/postdoctoral-position-in-multi-omics-machine-learning/) | postdoc | Sweden | 2026-11-15 |
| 🔴 **1d** | [Postdoc in Vertebrate Genome Assembly and Comparative Genomics University of Copenhagen · ](https://www.openpostdoc.org/position/533e724f-9e48-41e0-af4f-ccf198ca221a) | postdoc | International | 2026-11-15 |
| 🔴 **1d** | [Postdoc in multi-omics machine learning and computational cancer biology KTH](https://www.scilifelab.se/career/postdoc-in-multi-omics-machine-learning-and-computational-cancer-biology/) | postdoc | Sweden | 2026-11-15 |
| 🔴 **1d** | [Research Associate/Fellow in RNA Biology at University of Nottingham, UK](https://researchersjob.com/research-associate-fellow-in-rna-biology/) | postdoc | United Kingdom | 2026-11-15 |
| 🔴 **1d** | [Research Associate Vacancy at ICRISAT Hyderabad / PhD Fresher Apply Now](https://www.biotecnika.org/2026/10/icrisat-research-associate-vacancy-oilseeds-pre-breeding-genomics/) | postdoc | India | 2026-11-15 |
| 🔴 **2d** | [Research Associate in Cancer Biology](https://www.jobs.ac.uk/job/DTK336/research-associate-in-cancer-biology) | postdoc | United Kingdom | 2026-11-16 |
| 🔴 **2d** | [Associate or Senior Editor, Genome Biology](https://www.nature.com/naturecareers/job/12866256/associate-or-senior-editor-genome-biology/?LinkSource=PremiumListing) | other | International | 2026-11-16 |
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
