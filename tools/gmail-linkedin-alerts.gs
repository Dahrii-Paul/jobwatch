/**
 * JobWatch — LinkedIn job alerts → your JobWatch dashboard
 * ---------------------------------------------------------
 * Runs inside YOUR Gmail (Google Apps Script). Every hour it looks for LinkedIn
 * job-alert e-mails, pulls out each job (title, company, location, link) and
 * sends them to your JobWatch repo, which scores them and adds the matching
 * ones to your dashboard and feed.
 *
 * It reads only (a) LinkedIn job-alert e-mails and (b) e-mails YOU send to
 * yourself with "jobwatch" in the subject (a quick way to save posts from X,
 * ResearchGate, WhatsApp...: Share → Gmail → to yourself, subject
 * "jobwatch: <job title>"). Each processed e-mail gets the Gmail label
 * "jobwatch-sent"; nothing else in your mailbox is read or sent anywhere.
 *
 * SETUP (once) — see the README section "LinkedIn job alerts":
 *   1. Paste this file into a new project at https://script.google.com
 *   2. Project Settings → Script properties → add  GITHUB_TOKEN = <your token>
 *   3. Run  testWithoutSending  → check the log shows your alert jobs
 *   4. Run  installHourlyCheck  → done
 */

const REPO = 'Dahrii-Paul/jobwatch';
const LABEL = 'jobwatch-sent';
const SEARCH = 'from:(jobalerts-noreply@linkedin.com OR jobs-noreply@linkedin.com OR ' +
               'jobs-listings@linkedin.com) newer_than:7d -label:' + LABEL;
// e-mails you send yourself: Share → Gmail, subject starting with "jobwatch"
const SHARE_SEARCH = 'from:me subject:jobwatch newer_than:7d -label:' + LABEL;
const BATCH = 50;

/** Main job: find new alert e-mails, send their jobs, label them. */
function checkAlerts() {
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) throw new Error('Add GITHUB_TOKEN under Project Settings → Script properties first.');
  const label = GmailApp.getUserLabelByName(LABEL) || GmailApp.createLabel(LABEL);
  const threads = GmailApp.search(SEARCH, 0, 50);
  let jobs = [];
  threads.forEach(t => t.getMessages().forEach(m => {
    jobs = jobs.concat(parseAlert(m.getPlainBody(), m.getBody()));
  }));
  const shared = GmailApp.search(SHARE_SEARCH, 0, 50);
  shared.forEach(t => t.getMessages().forEach(m => {
    const j = parseShare(m.getSubject(), m.getPlainBody());
    if (j) jobs.push(j);
  }));
  jobs = dedupe(jobs);
  for (let i = 0; i < jobs.length; i += BATCH) {
    sendToGitHub(token, jobs.slice(i, i + BATCH));
  }
  threads.concat(shared).forEach(t => t.addLabel(label));
  console.log(`Sent ${jobs.length} jobs from ${threads.length} alert e-mails and ${shared.length} shared e-mails`);
}

/** Dry run: shows what would be sent, sends nothing, labels nothing. */
function testWithoutSending() {
  const threads = GmailApp.search(SEARCH.replace(' -label:' + LABEL, ''), 0, 10);
  let jobs = [];
  threads.forEach(t => t.getMessages().forEach(m => {
    jobs = jobs.concat(parseAlert(m.getPlainBody(), m.getBody()));
  }));
  GmailApp.search(SHARE_SEARCH.replace(' -label:' + LABEL, ''), 0, 10).forEach(t => t.getMessages().forEach(m => {
    const j = parseShare(m.getSubject(), m.getPlainBody());
    if (j) jobs.push(j);
  }));
  jobs = dedupe(jobs);
  console.log(`${threads.length} LinkedIn alert e-mails found; ${jobs.length} jobs in total (incl. shared):`);
  jobs.forEach(j => console.log(`• ${j.title} | ${j.company} | ${j.location} | ${j.url}`));
  if (!threads.length) console.log('No alert e-mails yet — turn on LinkedIn job alerts and wait for the first one.');
}

/** Run once: checks every hour from now on. */
function installHourlyCheck() {
  ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'checkAlerts')
    .forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('checkAlerts').timeBased().everyHours(1).create();
  console.log('Installed: checkAlerts will run every hour.');
}

function sendToGitHub(token, jobs) {
  const res = UrlFetchApp.fetch(`https://api.github.com/repos/${REPO}/dispatches`, {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + token, Accept: 'application/vnd.github+json' },
    payload: JSON.stringify({ event_type: 'email-alert-jobs', client_payload: { jobs: jobs } }),
    muteHttpExceptions: true,
  });
  if (res.getResponseCode() >= 300) {
    throw new Error(`GitHub said ${res.getResponseCode()}: ${res.getContentText().slice(0, 200)} — ` +
                    'check the token has Contents: Read and write on ' + REPO);
  }
}

// ───────────── parsing (plain functions, no Gmail needed) ─────────────

const VIEW_JOB = /https?:\/\/(?:www\.)?linkedin\.com\/(?:comm\/)?jobs\/view\/(\d+)[^\s"'<>)]*/i;
const SKIP_TEXT = /^(view job|apply|easy apply|see all jobs|see jobs|actively recruiting|promoted|new|\d+ (applicants?|connections?).*|be an early applicant|.*school alumni.*|.*ago)$/i;

function parseAlert(plain, html) {
  const fromText = parsePlain(plain || '');
  return fromText.length ? fromText : parseHtml(html || '');
}

/** Plain-text alerts list each job as: title / company / location / "View job: <url>". */
function parsePlain(text) {
  const lines = text.split(/\r?\n/).map(s => s.trim());
  const out = [];
  lines.forEach((line, i) => {
    const m = line.match(VIEW_JOB);
    if (!m) return;
    const before = [];
    for (let k = i - 1; k >= 0 && before.length < 4; k--) {
      const s = lines[k];
      if (!s || /^-{3,}|^={3,}/.test(s)) { if (before.length) break; else continue; }
      if (VIEW_JOB.test(s) || SKIP_TEXT.test(s)) continue;
      before.unshift(s.replace(/^View job:?\s*/i, ''));
    }
    if (!before.length) return;
    out.push({ url: m[0], title: before[0], company: before[1] || '', location: before[2] || '',
               via: 'linkedin-alert' });
  });
  return out;
}

/** HTML fallback: the link text of each /jobs/view/<id> link is the job title. */
function parseHtml(html) {
  const out = [];
  const re = /<a\b[^>]*href="([^"]*linkedin\.com\/(?:comm\/)?jobs\/view\/\d+[^"]*)"[^>]*>([\s\S]*?)<\/a>/gi;
  let m;
  while ((m = re.exec(html))) {
    const text = m[2].replace(/<[^>]+>/g, ' ').replace(/&amp;/g, '&').replace(/&#39;|&rsquo;/g, "'")
                     .replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
    if (text.length < 4 || SKIP_TEXT.test(text)) continue;
    out.push({ url: m[1].replace(/&amp;/g, '&'), title: text, company: '', location: '', via: 'linkedin-alert' });
  }
  return out;
}

/** An e-mail you sent yourself: subject "jobwatch: Postdoc in genomics, IISc", body has the link. */
function parseShare(subject, body) {
  const url = ((body || '').match(/https?:\/\/[^\s<>"')]+/) || [])[0];
  if (!url) return null;
  let title = (subject || '').replace(/^\s*(fwd?:|re:)\s*/i, '').replace(/^\s*jobwatch\s*[:\-–—]?\s*/i, '').trim();
  const text = (body || '').replace(url, ' ').replace(/\s+/g, ' ').trim();
  if (title.length < 4) title = text.slice(0, 120);          // no title typed: use the shared post's text
  if (title.length < 4) title = 'Saved post: ' + url.replace(/^https?:\/\//, '').slice(0, 60);
  return { url: url, title: title, company: '', location: text.slice(0, 500), via: 'email-share' };
}

function dedupe(jobs) {
  const seen = {};
  return jobs.filter(j => {
    const id = (j.url.match(/jobs\/view\/(\d+)/) || [])[1] || j.url;
    if (seen[id]) return false;
    seen[id] = true;
    return true;
  });
}

if (typeof module !== 'undefined') module.exports = { parsePlain, parseHtml, parseAlert, parseShare, dedupe };
