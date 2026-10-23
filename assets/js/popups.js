// popups.js — gwern.net-style popups for footnotes and same-site references.
// Hovering a footnote marker shows the note in a popup with a mini title bar
// (close / collapse / pin); clicking the marker still jumps to the note at the
// bottom of the page. Popups can be pinned (stay open) and dragged by their
// title bar. Frame design follows gwern.net's popups (CC0/MIT); this code is
// our own. No JS: markers are plain links to the notes, which still works.
(function () {
  "use strict";

  var isTouch = window.matchMedia("(hover: none)").matches;
  var SHOW_DELAY = 150;
  var HIDE_DELAY = 250;

  var transient = null; // the one unpinned popup, if any: { box, target }
  var showTimer = null;
  var hideTimer = null;
  var zTop = 50;
  var pageCache = Object.create(null);

  var ICONS = {
    close:
      '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1.5" y="1.5" width="13" height="13" fill="none" stroke="currentColor"/>' +
      '<path d="M5 5l6 6M11 5l-6 6" stroke="currentColor" stroke-width="1.4"/></svg>',
    collapse:
      '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1.5" y="1.5" width="13" height="13" fill="none" stroke="currentColor"/>' +
      '<path d="M4.5 11h7" stroke="currentColor" stroke-width="1.6"/></svg>',
    pin:
      '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 1.5h6M6.2 1.5v5.2L3.5 9.6h9L9.8 6.7V1.5M8 9.6V15" ' +
      'fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>',
  };

  function clearTimers() {
    if (showTimer) { clearTimeout(showTimer); showTimer = null; }
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  }

  function setHighlight(box, on) {
    (box._highlights || []).forEach(function (el) {
      el.classList.toggle("highlighted", on);
    });
  }

  function removePopup(box) {
    if (!box || box._removed) return;
    box._removed = true;
    if (transient && transient.box === box) transient = null;
    if (box._target && box._target._pinnedPopup === box) box._target._pinnedPopup = null;
    setHighlight(box, false);
    box.classList.remove("popup-visible");
    setTimeout(function () { box.remove(); }, 120);
  }

  function closeTransient() {
    if (transient) removePopup(transient.box);
  }

  function scheduleHide() {
    clearTimers();
    if (!transient) return;
    var box = transient.box;
    hideTimer = setTimeout(function () { removePopup(box); }, HIDE_DELAY);
  }

  function bringToFront(box) {
    box.style.zIndex = ++zTop;
  }

  function togglePin(box) {
    if (box.classList.contains("pinned")) {
      box.classList.remove("pinned");
      if (box._target) box._target._pinnedPopup = null;
      if (transient && transient.box !== box) closeTransient();
      transient = { box: box, target: box._target };
    } else {
      box.classList.add("pinned");
      if (box._target) box._target._pinnedPopup = box;
      if (transient && transient.box === box) transient = null;
    }
  }

  function startDrag(event, box) {
    if (event.button !== 0 || event.target.closest("button")) return;
    event.preventDefault();
    if (!box.classList.contains("pinned")) togglePin(box); // dragging pins it
    bringToFront(box);
    var startX = event.pageX;
    var startY = event.pageY;
    var originLeft = parseFloat(box.style.left) || 0;
    var originTop = parseFloat(box.style.top) || 0;
    box.classList.add("dragging");
    function move(e) {
      box.style.left = originLeft + e.pageX - startX + "px";
      box.style.top = originTop + e.pageY - startY + "px";
    }
    function up() {
      box.classList.remove("dragging");
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", up);
    }
    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", up);
  }

  // title == null gives the mini title bar (buttons only), as gwern.net
  // uses for footnotes.
  function makePopup(title) {
    var box = document.createElement("div");
    box.className = "popup " + (title == null ? "mini-title-bar" : "has-title-bar");

    var bar = document.createElement("div");
    bar.className = "popframe-title-bar";
    [["close", "Close"], ["collapse", "Collapse"], ["pin", "Pin (keep open)"]].forEach(function (b) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "popframe-title-bar-button " + b[0] + "-button";
      btn.title = b[1];
      btn.setAttribute("aria-label", b[1]);
      btn.innerHTML = ICONS[b[0]];
      bar.appendChild(btn);
    });
    var titleEl = null;
    if (title != null) {
      var titleWrap = document.createElement("div");
      titleWrap.className = "popframe-title";
      titleEl = document.createElement("span");
      titleEl.textContent = title;
      titleWrap.appendChild(titleEl);
      bar.appendChild(titleWrap);
    }

    var scroll = document.createElement("div");
    scroll.className = "popframe-scroll-view";
    var content = document.createElement("div");
    content.className = "popframe-content-view";
    scroll.appendChild(content);
    box.appendChild(bar);
    box.appendChild(scroll);

    bar.querySelector(".close-button").addEventListener("click", function () { removePopup(box); });
    bar.querySelector(".collapse-button").addEventListener("click", function () {
      box.classList.toggle("collapsed");
    });
    bar.querySelector(".pin-button").addEventListener("click", function () { togglePin(box); });
    bar.addEventListener("mousedown", function (e) { startDrag(e, box); });
    box.addEventListener("mousedown", function () { bringToFront(box); });
    box.addEventListener("mouseenter", function () {
      if (transient && transient.box === box) clearTimers();
    });
    box.addEventListener("mouseleave", function () {
      if (transient && transient.box === box) scheduleHide();
    });

    return { box: box, content: content, titleEl: titleEl };
  }

  function position(box, anchorEl) {
    var r = anchorEl.getBoundingClientRect();
    var bw = box.offsetWidth;
    var bh = box.offsetHeight;
    var vw = document.documentElement.clientWidth;
    var vh = document.documentElement.clientHeight;

    // Below the marker; flip above if there isn't room below but is above.
    var top;
    if (vh - r.bottom < bh + 16 && r.top > bh + 16) {
      top = window.scrollY + r.top - bh - 10;
      box.classList.add("popup-above");
    } else {
      top = window.scrollY + r.bottom + 10;
      box.classList.remove("popup-above");
    }
    var left = window.scrollX + r.left - 24;
    if (left + bw > window.scrollX + vw - 16) left = window.scrollX + vw - bw - 16;
    if (left < window.scrollX + 8) left = window.scrollX + 8;
    box.style.top = top + "px";
    box.style.left = left + "px";
  }

  function show(target, build, highlights) {
    clearTimers();
    if (transient && transient.target === target) return null;
    if (target._pinnedPopup) {
      bringToFront(target._pinnedPopup);
      return null;
    }
    closeTransient();
    var p = build();
    p.box._target = target;
    p.box._highlights = highlights || [target];
    setHighlight(p.box, true);
    document.body.appendChild(p.box);
    bringToFront(p.box);
    position(p.box, target);
    requestAnimationFrame(function () { p.box.classList.add("popup-visible"); });
    transient = { box: p.box, target: target };
    return p;
  }

  // --- footnotes: content is already on the page, in section.footnotes ---
  function bindFootnoteRef(ref) {
    var note = document.getElementById((ref.getAttribute("href") || "").slice(1));
    if (!note) return;

    ref.addEventListener("mouseenter", function () {
      clearTimers();
      showTimer = setTimeout(function () {
        show(ref, function () {
          var p = makePopup(null);
          var clone = note.cloneNode(true);
          clone.querySelectorAll(".footnote-back").forEach(function (el) { el.remove(); });
          p.content.innerHTML = clone.innerHTML;
          p.box.classList.add("footnote-popup");
          return p;
        }, [ref, note]);
      }, SHOW_DELAY);
    });
    ref.addEventListener("mouseleave", scheduleHide);
    ref.addEventListener("click", function () {
      clearTimers();
      closeTransient();
    });
  }

  // --- same-site references: fetch the page, show its #fragment or abstract ---
  function fetchFragment(url, fragmentId) {
    var p = pageCache[url];
    if (!p) {
      p = fetch(url)
        .then(function (res) {
          if (!res.ok) throw new Error("fetch failed: " + res.status);
          return res.text();
        })
        .then(function (html) {
          return new DOMParser().parseFromString(html, "text/html");
        });
      pageCache[url] = p;
    }
    return p.then(function (doc) {
      var el = null;
      if (fragmentId) el = doc.getElementById(fragmentId);
      if (!el) el = doc.querySelector(".abstract");
      if (!el) el = doc.querySelector("main.article .content p");
      var titleEl = doc.querySelector(".page-meta h1, title");
      return {
        title: titleEl ? titleEl.textContent.replace(/\s+/g, " ").trim() : url,
        html: el ? el.innerHTML : "<p><em>No preview available.</em></p>",
      };
    });
  }

  function bindPopupRef(link) {
    var href = link.getAttribute("href");
    if (!href) return;
    var url = new URL(href, window.location.href);
    if (url.origin !== window.location.origin) return;
    var fragmentId = url.hash ? url.hash.slice(1) : null;
    var pagePath = url.pathname + url.search;

    link.addEventListener("mouseenter", function () {
      clearTimers();
      showTimer = setTimeout(function () {
        var p = show(link, function () {
          var q = makePopup("Loading…");
          q.content.innerHTML = '<p class="popup-loading">Fetching reference…</p>';
          return q;
        });
        if (!p) return;
        fetchFragment(pagePath, fragmentId).then(
          function (data) {
            if (p.box._removed) return;
            p.titleEl.textContent = data.title;
            p.content.innerHTML = data.html;
            var more = document.createElement("p");
            var a = document.createElement("a");
            a.href = href;
            a.textContent = "Read in full →";
            more.appendChild(a);
            more.style.fontSize = "0.85em";
            p.content.appendChild(more);
            if (!p.box.classList.contains("pinned")) position(p.box, link);
          },
          function () {
            if (!p.box._removed) p.content.innerHTML = '<p class="popup-loading">Couldn’t load preview.</p>';
          }
        );
      }, 180);
    });
    link.addEventListener("mouseleave", scheduleHide);
  }

  function init() {
    // Touch screens: no hover, so markers and links just navigate (tapping a
    // footnote marker jumps to the note; its ↑ jumps back).
    if (isTouch) return;
    document.querySelectorAll("a.footnote-ref").forEach(bindFootnoteRef);
    document.querySelectorAll("a.popup-ref").forEach(bindPopupRef);
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      clearTimers();
      document.querySelectorAll(".popup").forEach(removePopup);
    });
    document.addEventListener("scroll", function () {
      clearTimers();
      closeTransient();
    }, { passive: true });
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
