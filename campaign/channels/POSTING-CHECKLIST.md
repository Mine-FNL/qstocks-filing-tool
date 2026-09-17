# Posting checklist — first launch

A short checklist to print or keep open in another tab while you
execute the launches.

## T-3 days — prep

- [ ] Confirm HN account has a visible profile (bio, real or work
      email, no obviously new-account flags). HN penalises Show HN
      posts from accounts created < 6 months ago with no comment
      history. If your account is young: post 3-4 high-quality
      comments elsewhere on HN first, then do the Show HN.
- [ ] Reddit account warmup: same story. /r/MachineLearning removes
      first-time posters' links to GitHub aggressively. If your
      account has < 50 karma, post 2-3 comments in non-self threads
      first.
- [ ] X / LinkedIn: if you have an existing audience, do not change
      anything about the accounts. Same handles, same profile, just
      compose-and-submit.

## T-1 day — final check

- [ ] Read `campaign/channels/show-hn.md` one more time. Make ONE
      personal edit pass — your voice, not mine. The draft is
      polished; the post must sound like you, not a template.
- [ ] Re-run `python qscreen_eval.py` locally; capture the SHA-256
      of the bench.json. Have this number ready — if HN asks for the
      specific bench SHA you'll need it.
- [ ] Open `https://github.com/Mine-FNL/qstocks-filing-tool` in an
      incognito window and verify the README hero image renders.
      (If it 404s on the cover-image domain, fall back to the
      demo-flow-16x9.jpg alone.)

## T-0 — posting (Tue–Thu 08:00–10:00 ET)

- [ ] Open https://news.ycombinator.com/submit
- [ ] Click "Show HN"
- [ ] Paste **Title** from `HN-FINAL.md`
- [ ] Paste **Body** from `HN-FINAL.md`
- [ ] **Leave URL field empty** (repo URL is in the body text — Show HN convention)
- [ ] Solve the captcha (have patience; HN's captcha rounds suck)
- [ ] Click Submit
- [ ] Copy the resulting HN post URL into a notepad for the cross-link step

## T+30m — quick triage

- [ ] Refresh the post; reply to the first 2-3 substantive comments
      using the pre-reply snippets in `HN-FINAL.md`
- [ ] Don't reply to drive-by critics — they usually self-resolve
      or get downvoted by the rest of the thread
- [ ] Don't delete the post

## T+12h — check velocity

- [ ] If upvotes >= 30 by +12h: you have a hit; let it run; prepare
      to cross-link on X with the HN permalink
- [ ] If upvotes < 10 by +12h: the post is "running normally"; go
      to the Reddit cross-posts (campaign/channels/reddit-*.md) but
      space them 24 h apart, do NOT post all three at once

## T+24h — X thread (15 tweets)

- [ ] Use `campaign/channels/x-thread.md`. Each tweet is
      self-contained — drop into Twitter one-by-one with ~30 min
      spacing between tweets 1-10; tweets 11-15 spread over the
      remaining week
- [ ] Lead image: stats-card-16x9.jpg OR the demo-promo-6s.mp4
      (Twitter now supports short MP4 embeds via `x.com/i/status/<id>`
      with the embedded video player)
- [ ] Quote-tweet the HN permalink in tweet 14 (not tweet 1 — the
      HN URL at the top makes the thread look like an ad)

## T+48h — Reddit

- [ ] r/MachineLearning (campaign/channels/reddit-ml.md)
- [ ] T+96h — r/quant (campaign/channels/reddit-quant.md)
- [ ] In the r/MachineLearning selftext, link to the HN thread at
      the bottom ("Cross-posted to HN: <url>"); this is allowed by
      both communities if framed honestly

## T+7 days — LinkedIn

- [ ] Use `campaign/channels/linkedin.md`
- [ ] LinkedIn algorithm rewards first-hour engagement more than
      first-day; the window to hit the most-connected people is
      the first 60 min

## After 30 days

- [ ] Whatever the upper bound on stars is, you've harvested.
      Either the post worked or it didn't. If it did, the second
      post in 3 months will land easier because you'll have a
      track record. If it didn't, look at where the conversation
      stalled (usually: missing installers, missing jurisdiction
      profile, missing evaluator) and ship that.

## If something breaks

- HN post got removed (very rare for Show HN): DM @dang on X with
  the URL and ask why. Be respectful.
- Reddit post auto-removed by spam filter: modmail the
  /r/MachineLearning or /r/quant mod queue with the exact text
  you submitted. Provide the GitHub repo URL. They will usually
  reinstate within 4 hours if you're a known user.
- Anyone flags "this is an ad" in comments: reply with a one-line
  "you're right to ask — everything we say here is verifiable at
  <commit SHA> in the repo. The project is open-source and we don't
  have a paid tier." Then stop replying.
