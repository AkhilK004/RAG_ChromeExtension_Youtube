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

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "GET_VIDEO_ID") {
    sendResponse({ videoId: getVideoIdFromUrl(window.location.href) });
  }

  if (msg.type === "SEEK_TO") {
    const ok = seekTo(Number(msg.seconds || 0));
    sendResponse({ ok });
  }
});