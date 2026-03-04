function getVideoIdFromUrl(url) {
  try {
    const u = new URL(url);
    return u.searchParams.get("v");
  } catch {
    return null;
  }
}

function seekTo(seconds) {
  const video = document.querySelector("video");
  if (!video) return false;
  video.currentTime = Math.max(0, seconds);
  video.play?.();
  return true;
}

/** -------- transcript helpers -------- **/

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function fmtTimeToBracket(t) {
  // Converts "3:07" or "01:02:03" -> "[03:07]" or "[01:02:03]"
  if (!t) return "[00:00]";
  const parts = t.trim().split(":").map((p) => p.trim());
  if (parts.length === 2) {
    const [m, s] = parts;
    return `[${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}]`;
  }
  if (parts.length === 3) {
    const [h, m, s] = parts;
    return `[${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}]`;
  }
  return `[${t}]`;
}

async function openTranscriptPanel() {
  // Try to open YouTube transcript panel via UI clicks.
  // Works best on watch pages. YouTube UI changes frequently, so we try multiple selectors.

  // 1) Click the "..." (More actions) button
  const moreBtn =
    document.querySelector('button[aria-label*="More actions"]') ||
    document.querySelector('button[aria-label*="More"]') ||
    document.querySelector('ytd-menu-renderer button[aria-label*="More"]');

  if (!moreBtn) return false;
  moreBtn.click();
  await sleep(400);

  // 2) Find "Show transcript" in the menu
  const items = Array.from(document.querySelectorAll("ytd-menu-service-item-renderer, tp-yt-paper-item"));
  const transcriptItem = items.find((el) => {
    const txt = (el.innerText || "").trim().toLowerCase();
    return txt.includes("transcript");
  });

  if (!transcriptItem) {
    // Menu not found or transcript not available
    // Close menu by clicking outside
    document.body.click();
    return false;
  }

  transcriptItem.click();
  await sleep(800);

  return true;
}

function scrapeTranscriptFromDom() {
  // YouTube transcript rows usually live inside ytd-transcript-segment-renderer
  const rows = Array.from(document.querySelectorAll("ytd-transcript-segment-renderer"));

  if (!rows.length) return null;

  const lines = [];
  for (const r of rows) {
    const timeEl =
      r.querySelector("#segment-timestamp") ||
      r.querySelector(".segment-timestamp") ||
      r.querySelector("div.segment-timestamp");

    const textEl =
      r.querySelector("#segment-text") ||
      r.querySelector(".segment-text") ||
      r.querySelector("yt-formatted-string");

    const ts = (timeEl?.innerText || "").trim();
    const text = (textEl?.innerText || "").replace(/\s+/g, " ").trim();

    if (!text) continue;
    lines.push(`${fmtTimeToBracket(ts)} ${text}`);
  }

  if (!lines.length) return null;
  return lines.join("\n");
}

async function getTranscriptText() {
  // If transcript already visible, scrape it
  let transcript = scrapeTranscriptFromDom();
  if (transcript) return transcript;

  // Try opening transcript panel
  const opened = await openTranscriptPanel();
  if (opened) {
    transcript = scrapeTranscriptFromDom();
    if (transcript) return transcript;
  }

  // If still not found, return null
  return null;
}

/** -------- message bridge -------- **/

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "GET_VIDEO_ID") {
    sendResponse({ videoId: getVideoIdFromUrl(window.location.href) });
    return true;
  }

  if (msg.type === "SEEK_TO") {
    const ok = seekTo(Number(msg.seconds || 0));
    sendResponse({ ok });
    return true;
  }

  if (msg.type === "GET_TRANSCRIPT") {
    (async () => {
      const transcript = await getTranscriptText();
      sendResponse({ transcript }); // string or null
    })();
    return true; // keep message channel open for async
  }
});