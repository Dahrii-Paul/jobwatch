# [JobWatch](https://dahrii-paul.github.io/jobwatch/) 🧬

**An AI job-search agent for bioinformatics, computational biology and genomics.**
It watches Indian recruitment portals (ICMR, DBT/BRIC, DST, CSIR, ICAR/ASRB, UPSC, institutes) for **permanent Scientist and Assistant Professor posts**, and Indian + international sites (SciLifeLab, EURAXESS, jobs.ac.uk, Nature Careers, universities in Sweden, the Netherlands, Switzerland, Germany, Denmark, Austria, Singapore, Australia, UK) for **postdocs and fellowships** — with deadlines.

Runs free on GitHub Actions twice a day, publishes a dashboard on GitHub Pages, and opens a GitHub issue (which GitHub e-mails you) whenever new matches appear.

<!-- STATS:START -->
## Live stats · updated 2026-11-03 23:40

| Metric | Count |
|---|---|
| 🎯 Open matches | **297** |
| 🏛️ Permanent posts — India | **78** |
| 🔬 Postdocs / fellowships — India | **17** |
| ✈️ Postdocs / fellowships — abroad | **118** |
| 🌍 Permanent / faculty — abroad | **35** |
| ⏰ Closing within 14 days | **56** |
| 🆕 New this run | **0** |
| 📡 Sources working | **165 / 209** |

### ⏳ Closing within 30 days

| Left | Position | Type | Where | Deadline |
|---|---|---|---|---|
| 🔴 **0d** | [Postdoc - Stem Cell Disease Modeling and Precision Medicine - Innovative Genomics Institut](https://www.openpostdoc.org/position/954b2f2c-b870-474d-842e-e719387ec589) | postdoc | International | 2026-11-03 |
| 🔴 **0d** | [Distinguished Professors, Young Faculty, Postdoctoral Researchers](https://www.nature.com/naturecareers/job/12862946/distinguished-professors-young-faculty-postdoctoral-researchers/?LinkSource=PremiumListing) | postdoc | China | 2026-11-03 |
| 🔴 **1d** | [PhD Scholarship in RNA Structure Computational Analysis at University of Copenhagen, Denma](https://researchersjob.com/phd-scholarship-in-rna-structure/) | phd | Denmark | 2026-11-04 |
| 🔴 **2d** | [Biological & Life Sciences Division – Postdoc Researcher: AI for Precision Medicine and Th](https://www.timeshighereducation.com/unijobs/listing/416237/biological-and-life-sciences-division-postdoc-researcher-ai-for-precision-medicine-and-therapeutics/?LinkSource=PremiumListing) | postdoc | United Arab Emirates | 2026-11-05 |
| 🔴 **2d** | [Biological and Life Sciences Division – Research Scientist: AI for Precision Medicine](https://www.timeshighereducation.com/unijobs/listing/416229/biological-and-life-sciences-division-research-scientist-ai-for-precision-medicine/?LinkSource=PremiumListing) | permanent | United Arab Emirates | 2026-11-05 |
| 🔴 **2d** | [Post-Doctoral Fellowship in Energy Metabolism Faculdade de Medicina de Ribeirão Preto - US](https://www.openpostdoc.org/position/121a48d2-1d31-472e-8cb2-11fe8cfcb22d) | postdoc | International | 2026-11-05 |
| 🔴 **2d** | [Postdoctoral Researcher in Immune-Metabolism and Multi-omics of Symptom Dimensions Univers](https://www.openpostdoc.org/position/62cab703-eb59-499d-a46b-32ed17557181) | postdoc | International | 2026-11-05 |
| 🔴 **3d** | [Postdoc Researcher AI/Machine Learn for Multimodal Cardiovasc Data (VASCUL-AID) Are you a ](https://www.academictransfer.com/en/jobs/365056/postdoc-researcher-aimachine-learn-for-multimodal-cardiovasc-data-vascul-aid/) | postdoc | Netherlands | 2026-11-06 |
| 🔴 **3d** | [Postdoc Employee – Systems Biology – Molecular & Cell Biology University of California, Be](https://www.openpostdoc.org/position/cd4ac711-a607-46d9-8047-b8dfa915d647) | postdoc | International | 2026-11-06 |
| 🔴 **3d** | [Project Research Scientist Position in ICMR (Non-medical): ,Mumbai India](https://researchersjob.com/scientist-position-in-icmr-2/) | project | India | 2026-11-06 |
| 🔴 **3d** | [Advertisement (English) ( 702.00 KB) View](https://www.icmr.gov.in/icmrobject/uploads/Recruitment/1791381461_eoimrhrus.pdf) | permanent | India | 2026-11-06 |
| 🔴 **3d** | [Advertisement (Hindi) ( 870.93 KB) View](https://www.icmr.gov.in/icmrobject/uploads/Recruitment/1791867744_expressionofinterestpdf.pdf) | permanent | India | 2026-11-06 |
| 🔴 **3d** | [Invitation for Expression of Interest for tenure-based deployment of regular DHR/ICMR Medi](https://www.icmr.gov.in/icmrobject/uploads/Recruitment/1791805428_39mrhrusinstatesuts.pdf) | permanent | India | 2026-11-06 |
| 🟠 **5d** | [Faculty Positions in Systems Hub, HKUST (GZ)](https://www.nature.com/naturecareers/job/12863219/faculty-positions-in-systems-hub-hkust-gz-/?LinkSource=PremiumListing) | permanent | Hong Kong | 2026-11-08 |
| 🟠 **5d** | [Research Associate - Urinary Tract Disease Research Group](https://www.timeshighereducation.com/unijobs/listing/416934/research-associate-urinary-tract-disease-research-group/?LinkSource=PremiumListing) | postdoc | Australia | 2026-11-08 |
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
