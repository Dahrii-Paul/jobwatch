# [JobWatch](https://dahrii-paul.github.io/jobwatch/) 🧬

**An AI job-search agent for bioinformatics, computational biology and genomics.**
It watches Indian recruitment portals (ICMR, DBT/BRIC, DST, CSIR, ICAR/ASRB, UPSC, institutes) for **permanent Scientist and Assistant Professor posts**, and Indian + international sites (SciLifeLab, EURAXESS, jobs.ac.uk, Nature Careers, universities in Sweden, the Netherlands, Switzerland, Germany, Denmark, Austria, Singapore, Australia, UK) for **postdocs and fellowships** — with deadlines.

Runs free on GitHub Actions twice a day, publishes a dashboard on GitHub Pages, and opens a GitHub issue (which GitHub e-mails you) whenever new matches appear.

<!-- STATS:START -->
## Live stats · updated 2026-11-03 22:16

| Metric | Count |
|---|---|
| 🎯 Open matches | **206** |
| 🏛️ Permanent posts — India | **60** |
| 🔬 Postdocs / fellowships — India | **13** |
| ✈️ Postdocs / fellowships — abroad | **61** |
| 🌍 Permanent / faculty — abroad | **24** |
| ⏰ Closing within 14 days | **30** |
| 🆕 New this run | **57** |
| 📡 Sources working | **100 / 163** |

### ⏳ Closing within 30 days

| Left | Position | Type | Where | Deadline |
|---|---|---|---|---|
| 🔴 **0d** | [Distinguished Professors, Young Faculty, Postdoctoral Researchers](https://www.nature.com/naturecareers/job/12862946/distinguished-professors-young-faculty-postdoctoral-researchers/?LinkSource=PremiumListing) | postdoc | China | 2026-11-03 |
| 🔴 **1d** | [PhD Scholarship in RNA Structure Computational Analysis at University of Copenhagen, Denma](https://researchersjob.com/phd-scholarship-in-rna-structure/) | phd | Denmark | 2026-11-04 |
| 🔴 **3d** | [Postdoc Researcher AI/Machine Learn for Multimodal Cardiovasc Data (VASCUL-AID) Are you a ](https://www.academictransfer.com/en/jobs/365056/postdoc-researcher-aimachine-learn-for-multimodal-cardiovasc-data-vascul-aid/) | postdoc | Netherlands | 2026-11-06 |
| 🔴 **3d** | [Project Research Scientist Position in ICMR (Non-medical): ,Mumbai India](https://researchersjob.com/scientist-position-in-icmr-2/) | project | India | 2026-11-06 |
| 🟠 **5d** | [Faculty Positions in Systems Hub, HKUST (GZ)](https://www.nature.com/naturecareers/job/12863219/faculty-positions-in-systems-hub-hkust-gz-/?LinkSource=PremiumListing) | permanent | Hong Kong | 2026-11-08 |
| 🟠 **5d** | [Postdoctoral Researcher in Real World Evidence for Knee Osteoarthritis at Novo Nordisk, De](https://researchersjob.com/postdoctoral-researcher-in-real-world-evidence/) | postdoc | Denmark | 2026-11-08 |
| 🟠 **5d** | [Postdoctoral Researcher in Machine Learning & Cheminformatics at VTT, Finland](https://researchersjob.com/postdoctoral-researcher-in-machine-learning-cheminformatics/) | postdoc | Finland | 2026-11-08 |
| 🟠 **5d** | [Bioinformatics Jobs at St. Johns with Rs. 72,000/- PM Pay / Freshers Eligible](https://www.biotecnika.org/2026/10/st-johns-bioinformatics-jobs-bangalore/) | project | India | 2026-11-08 |
| 🟠 **6d** | [Research Assistant - AI Scientist & Computational Cancer Biology](https://www.jobs.ac.uk/job/DTK666/research-assistant-ai-scientist-and-computational-cancer-biology) | permanent | United Kingdom | 2026-11-09 |
| 🟠 **7d** | [Bioinformatics Research Associate](https://www.jobs.ac.uk/job/DTG666/bioinformatics-research-associate) | postdoc | United Kingdom | 2026-11-10 |
| 🟠 **7d** | [IIT Bombay Postdoc Vacancy 2026 / Apply Online Now](https://www.biotecnika.org/2026/10/iit-bombay-postdoc-vacancy-2026/) | postdoc | India | 2026-11-10 |
| 🟠 **8d** | [Research Fellow (Maternity Cover)](https://www.jobs.ac.uk/job/DTM042/research-fellow-maternity-cover) | postdoc | United Kingdom | 2026-11-11 |
| 🟠 **8d** | [Research Associate Position at IIT Gandhinagar: India](https://researchersjob.com/research-associate-position-at-iit/) | postdoc | India | 2026-11-11 |
| 🟠 **8d** | [राष्ट्रीय सर्वेक्षण के लिए CDER द्वारा 'नेशनल ओरल हेल्थ प्रोग्राम' के अंतर्गत प्रोजेक्ट रि](https://zoombio.org/jobs/cder-i-vacancy-for-project-research-scientist-i-biostatistician-non-medical-field-based-if7bpck) | project | India | 2026-11-11 |
| 🟠 **9d** | [Post-doc position on Multi-omics Post-doc Position on Multi-omics in Hereditary Fibrinogen](https://www.academictransfer.com/en/jobs/364732/post-doc-position-on-multi-omics/) | postdoc | Netherlands | 2026-11-12 |
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
