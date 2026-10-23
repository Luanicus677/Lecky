// popups.js — hover/tap previews for footnotes and cross-page references.
// No framework. Degrades to plain anchor navigation with JS disabled.
(function () {
  "use strict";

  var isTouch = window.matchMedia("(hover: none)").matches;
  var activePopup = null;
  var pageCache = Object.create(null);
  var showTimer = null;
  var hideTimer = null;

  function clearTimers() {
    if (showTimer) { clearTimeout(showTimer); showTimer = null; }
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  }

  function removePopup() {
    if (activePopup) {
      activePopup.remove();
      activePopup = null;
    }
  }

  function positionNear(box, anchorEl) {
    var r = anchorEl.getBoundingClientRect();
    var top = window.scrollY + r.bottom + 8;
    var left = window.scrollX + r.left;
    document.body.appendChild(box);
    var bw = box.offsetWidth;
    var vw = document.documentElement.clientWidth;
    if (left + bw > window.scrollX + vw - 16) {
      left = window.scrollX + vw - bw - 16;
    }
    if (left < window.scrollX + 8) left = window.scrollX + 8;
    box.style.top = top + "px";
    box.style.left = left + "px";
  }

  function showBox(box, anchorEl) {
    removePopup();
    activePopup = box;
    box.className = "popup-box";
    positionNear(box, anchorEl);
    box.addEventListener("mouseenter", clearTimers);
    box.addEventListener("mouseleave", scheduleHide);
  }

  function scheduleHide() {
    clearTimers();
    hideTimer = setTimeout(removePopup, 220);
  }

  // --- local footnotes: content already in the DOM, just clone it ---
  function handleFootnoteRef(sup) {
    var link = sup.querySelector("a");
    if (!link) return;
    var id = link.getAttribute("href");
    if (!id || id.charAt(0) !== "#") return;
    // getElementById (not querySelector) because footnote ids contain
    // literal colons (e.g. "fn:sample"), which are invalid unescaped in
    // a CSS selector string.
    var target = document.getElementById(id.slice(1));
    if (!target) return;

    sup.addEventListener("mouseenter", function () {
      clearTimers();
      showTimer = setTimeout(function () {
        var box = document.createElement("div");
        var title = document.createElement("p");
        title.className = "popup-title";
        title.textContent = "Footnote";
        box.appendChild(title);
        var body = document.createElement("div");
        body.innerHTML = target.innerHTML.replace(
          /<a class="footnote-backref"[^>]*>.*?<\/a>/, ""
        );
        box.appendChild(body);
        showBox(box, sup);
      }, 140);
    });
    sup.addEventListener("mouseleave", scheduleHide);
  }

  // --- cross-page references: fetch same-origin page, extract #id or .abstract ---
  function fetchFragment(url, fragmentId) {
    var cacheKey = url;
    var p = pageCache[cacheKey];
    if (!p) {
      p = fetch(url)
        .then(function (res) {
          if (!res.ok) throw new Error("fetch failed: " + res.status);
          return res.text();
        })
        .then(function (html) {
          return new DOMParser().parseFromString(html, "text/html");
        });
      pageCache[cacheKey] = p;
    }
    return p.then(function (doc) {
      var el = null;
      if (fragmentId) el = doc.getElementById(fragmentId);
      if (!el) el = doc.querySelector(".abstract");
      if (!el) el = doc.querySelector("main.article .content p");
      var titleEl = doc.querySelector(".page-meta h1, title");
      return {
        title: titleEl ? titleEl.textContent.trim() : url,
        html: el ? el.innerHTML : "<p><em>No preview available.</em></p>",
      };
    });
  }

  function handlePopupRef(link) {
    var href = link.getAttribute("href");
    if (!href) return;
    var url = new URL(href, window.location.href);
    if (url.origin !== window.location.origin) return; // same-origin only
    var fragmentId = url.hash ? url.hash.slice(1) : null;
    var pagePath = url.pathname + url.search;

    link.addEventListener("mouseenter", function () {
      clearTimers();
      showTimer = setTimeout(function () {
        var box = document.createElement("div");
        var title = document.createElement("p");
        title.className = "popup-title";
        title.textContent = "Loading…";
        box.appendChild(title);
        var loading = document.createElement("p");
        loading.className = "popup-loading";
        loading.textContent = "Fetching reference…";
        box.appendChild(loading);
        showBox(box, link);

        fetchFragment(pagePath, fragmentId).then(
          function (data) {
            if (activePopup !== box) return;
            title.textContent = data.title;
            loading.remove();
            var body = document.createElement("div");
            body.innerHTML = data.html;
            box.appendChild(body);
            var more = document.createElement("p");
            more.innerHTML = '<a href="' + href + '">Read in full →</a>';
            more.style.marginTop = "0.6rem";
            more.style.fontSize = "0.82em";
            box.appendChild(more);
            positionNear(box, link);
          },
          function () {
            if (activePopup !== box) return;
            loading.textContent = "Couldn't load preview.";
          }
        );
      }, 180);
    });
    link.addEventListener("mouseleave", scheduleHide);
  }

  function init() {
    if (isTouch) return; // mobile/touch: plain navigation, no hover popups
    document.querySelectorAll("sup.footnote-ref").forEach(handleFootnoteRef);
    document.querySelectorAll("a.popup-ref").forEach(handlePopupRef);
    document.addEventListener(
      "scroll",
      function () {
        clearTimers();
        removePopup();
      },
      { passive: true }
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

// --- theme toggle (persisted) ---
(function () {
  "use strict";
  var KEY = "lecky-theme";
  function apply(theme) {
    if (theme === "dark" || theme === "light") {
      document.documentElement.setAttribute("data-theme", theme);
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  }
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  apply(saved);

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme");
      var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      var effectiveCurrent = current || (prefersDark ? "dark" : "light");
      var next = effectiveCurrent === "dark" ? "light" : "dark";
      apply(next);
      try { localStorage.setItem(KEY, next); } catch (e) {}
    });
  });
})();
