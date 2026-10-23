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
      var box = activePopup;
      activePopup = null;
      box.classList.remove("popup-visible");
      setTimeout(function () {
        box.remove();
      }, 120);
    }
  }

  function positionNear(box, anchorEl) {
    var r = anchorEl.getBoundingClientRect();
    var left = window.scrollX + r.left;
    document.body.appendChild(box);
    var bw = box.offsetWidth;
    var bh = box.offsetHeight;
    var vw = document.documentElement.clientWidth;
    var vh = document.documentElement.clientHeight;

    // Edge-flip: if there isn't room below the anchor but there is above,
    // show the popup above it instead of letting it run off-screen.
    var spaceBelow = vh - r.bottom;
    var top;
    if (spaceBelow < bh + 16 && r.top > bh + 16) {
      top = window.scrollY + r.top - bh - 8;
      box.classList.add("popup-above");
    } else {
      top = window.scrollY + r.bottom + 8;
      box.classList.remove("popup-above");
    }

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
    requestAnimationFrame(function () {
      box.classList.add("popup-visible");
    });
    box.addEventListener("mouseenter", clearTimers);
    box.addEventListener("mouseleave", scheduleHide);
  }

  function scheduleHide() {
    clearTimers();
    hideTimer = setTimeout(removePopup, 220);
  }

  // --- footnotes: now always-visible margin sidenotes (see sidenotes.js)
  // on wide screens, so no hover-popup is needed there -- the note is
  // already sitting right next to its marker. On narrow screens, where
  // the CSS hides sidenotes (@media max-width: 1180px in style.css),
  // tapping the marker toggles the note open inline instead. ---
  function handleFootnoteRef(sup) {
    var target = document.getElementById("sn:" + sup.id.replace(/^fnref:/, ""));
    if (!target) return;
    sup.addEventListener("click", function (event) {
      if (window.matchMedia("(min-width: 1181px)").matches) return; // handled by CSS/sidenotes.js
      event.preventDefault();
      target.classList.toggle("sidenote-inline-shown");
    });
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
        var title = document.createElement("div");
        title.className = "popup-title";
        title.textContent = "Loading…";
        box.appendChild(title);
        var bodyWrap = document.createElement("div");
        bodyWrap.className = "popup-body";
        var loading = document.createElement("p");
        loading.className = "popup-loading";
        loading.textContent = "Fetching reference…";
        bodyWrap.appendChild(loading);
        box.appendChild(bodyWrap);
        showBox(box, link);

        fetchFragment(pagePath, fragmentId).then(
          function (data) {
            if (activePopup !== box) return;
            title.textContent = data.title;
            loading.remove();
            var body = document.createElement("div");
            body.innerHTML = data.html;
            bodyWrap.appendChild(body);
            var more = document.createElement("p");
            more.innerHTML = '<a href="' + href + '">Read in full →</a>';
            more.style.marginTop = "0.6rem";
            more.style.fontSize = "0.82em";
            bodyWrap.appendChild(more);
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
    // Footnote tap-to-toggle works on touch too (it's a click handler,
    // and it's the narrow-screen fallback for notes the CSS hides there).
    document.querySelectorAll("sup.footnote-ref").forEach(handleFootnoteRef);

    // Cross-page hover-preview popups need a mouse; on touch, links just
    // navigate normally.
    if (!isTouch) {
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
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

// --- margin table of contents: built from <h2> headings, when there are
// enough of them to be worth a ToC. No-op on pages with fewer than 2. ---
(function () {
  "use strict";

  function slugify(text) {
    return text
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-");
  }

  function buildToc() {
    var content = document.querySelector("main.article .content");
    if (!content) return;
    var headings = Array.prototype.slice.call(content.querySelectorAll("h2"));
    if (headings.length < 2) return;

    var usedIds = {};
    var items = headings.map(function (h) {
      if (!h.id) {
        var base = slugify(h.textContent) || "section";
        var id = base;
        var n = 2;
        while (usedIds[id] || document.getElementById(id)) {
          id = base + "-" + n++;
        }
        h.id = id;
      }
      usedIds[h.id] = true;
      return h;
    });

    var toc = document.createElement("nav");
    toc.className = "margin-toc";
    toc.setAttribute("aria-label", "Table of contents");
    var label = document.createElement("p");
    label.className = "margin-toc-label";
    label.textContent = "Contents";
    toc.appendChild(label);
    var ol = document.createElement("ol");
    items.forEach(function (h) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = "#" + h.id;
      a.textContent = h.textContent;
      li.appendChild(a);
      ol.appendChild(li);
    });
    toc.appendChild(ol);

    content.insertBefore(toc, content.firstChild);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildToc);
  } else {
    buildToc();
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
