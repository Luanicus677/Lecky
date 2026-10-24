// popups.js — gwern.net-style popups for footnotes, same-site references,
// Wikipedia links, and translations.
// Hovering a footnote marker shows the note in a popup with a mini title bar
// (close / collapse / pin); clicking the marker still jumps to the note at the
// bottom of the page. Popups can be pinned (stay open) and dragged by their
// title bar. Links inside a popup get popups of their own, stacked on top of
// it, so a reader can follow a chain of references without leaving the page.
// Frame design follows gwern.net's popups (CC0/MIT); this code is our own.
// No JS: markers and links are plain links, and translations show inline.
(function () {
  "use strict";

  var isTouch = window.matchMedia("(hover: none)").matches;
  var SHOW_DELAY = 150;
  var HIDE_DELAY = 250;

  // Unpinned popups, outermost first. A popup opened from a link inside
  // another popup records that popup as its _parentBox.
  var chain = [];
  var showTimer = null;
  var hideTimer = null;
  var zTop = 50;
  var pageCache = Object.create(null);
  var wikiCache = Object.create(null);

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

  function clearShow() {
    if (showTimer) { clearTimeout(showTimer); showTimer = null; }
  }

  function setHighlight(box, on) {
    (box._highlights || []).forEach(function (el) {
      el.classList.toggle("highlighted", on);
    });
  }

  function ancestors(box) {
    var list = [];
    for (; box; box = box._parentBox) list.push(box);
    return list;
  }

  function removePopup(box) {
    if (!box || box._removed) return;
    box._removed = true;
    chain.slice().forEach(function (b) {
      if (b._parentBox === box) removePopup(b);
    });
    var i = chain.indexOf(box);
    if (i >= 0) chain.splice(i, 1);
    if (box._target && box._target._popup === box) box._target._popup = null;
    setHighlight(box, false);
    box.classList.remove("popup-visible");
    setTimeout(function () { box.remove(); }, 120);
  }

  // Close every unpinned popup except `keep` and the popups it sits on.
  function trimChain(keep) {
    var stay = ancestors(keep);
    chain.slice().forEach(function (b) {
      if (stay.indexOf(b) < 0) removePopup(b);
    });
  }

  // After a short delay, keep the popups up to the innermost one the mouse is
  // over (or over the link that opened it), and close the rest.
  function scheduleHide() {
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(function () {
      hideTimer = null;
      var keep = null;
      for (var i = chain.length - 1; i >= 0 && !keep; i--) {
        var b = chain[i];
        if (b.matches(":hover") || (b._target && b._target.matches(":hover"))) keep = b;
      }
      if (!keep) keep = document.querySelector(".popup.pinned:hover");
      trimChain(keep);
    }, HIDE_DELAY);
  }

  function bringToFront(box) {
    box.style.zIndex = ++zTop;
  }

  function togglePin(box) {
    var i = chain.indexOf(box);
    if (box.classList.contains("pinned")) {
      box.classList.remove("pinned");
      if (i < 0) chain.push(box);
    } else {
      box.classList.add("pinned");
      if (i >= 0) chain.splice(i, 1);
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
    box.addEventListener("mouseleave", scheduleHide);

    return { box: box, content: content, titleEl: titleEl };
  }

  function position(box, anchorEl) {
    var r = anchorEl.getBoundingClientRect();
    var bw = box.offsetWidth;
    var bh = box.offsetHeight;
    var vw = document.documentElement.clientWidth;
    var vh = document.documentElement.clientHeight;

    // Below the anchor; flip above if there isn't room below but is above.
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
    clearShow();
    if (target._popup && !target._popup._removed) {
      bringToFront(target._popup);
      return null;
    }
    var parentBox = target.closest(".popup");
    trimChain(parentBox);
    var p = build();
    p.box._target = target;
    p.box._parentBox = parentBox;
    p.box._highlights = highlights || [target];
    target._popup = p.box;
    setHighlight(p.box, true);
    document.body.appendChild(p.box);
    bringToFront(p.box);
    position(p.box, target);
    requestAnimationFrame(function () { p.box.classList.add("popup-visible"); });
    chain.push(p.box);
    return p;
  }

  // Shared hover wiring: show after a delay, schedule hiding on leave.
  function onHover(el, delay, open) {
    el.addEventListener("mouseenter", function () {
      clearShow();
      showTimer = setTimeout(open, delay);
    });
    el.addEventListener("mouseleave", function () {
      clearShow();
      scheduleHide();
    });
  }

  function fillContent(p, html, foreign) {
    p.content.innerHTML = html;
    bindAll(p.content, foreign);
  }

  // --- footnotes: content is already on the page, in section.footnotes ---
  function bindFootnoteRef(ref) {
    var note = document.getElementById((ref.getAttribute("href") || "").slice(1));
    if (!note) return;
    onHover(ref, SHOW_DELAY, function () {
      var p = show(ref, function () { return makePopup(null); }, [ref, note]);
      if (!p) return;
      var clone = note.cloneNode(true);
      clone.querySelectorAll(".footnote-back").forEach(function (el) { el.remove(); });
      p.box.classList.add("footnote-popup");
      fillContent(p, clone.innerHTML, false);
      position(p.box, ref);
    });
    ref.addEventListener("click", function () {
      clearShow();
      trimChain(ref.closest(".popup"));
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
          var doc = new DOMParser().parseFromString(html, "text/html");
          // Make the fetched page's relative links absolute, so they still
          // point to the right place once shown inside this page.
          var base = new URL(url, window.location.href);
          doc.querySelectorAll("a[href]").forEach(function (a) {
            a.setAttribute("href", new URL(a.getAttribute("href"), base).href);
          });
          doc.querySelectorAll("img[src]").forEach(function (img) {
            img.setAttribute("src", new URL(img.getAttribute("src"), base).href);
          });
          return doc;
        });
      pageCache[url] = p;
    }
    return p.then(function (doc) {
      var el = null;
      if (fragmentId) el = doc.getElementById(fragmentId);
      if (!el) el = doc.querySelector(".abstract");
      if (!el) el = doc.querySelector("main.article .content p");
      var titleEl = doc.querySelector(".page-meta h1") || doc.querySelector("title");
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

    onHover(link, 180, function () {
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
          fillContent(p, data.html, true);
          var more = document.createElement("p");
          more.className = "popup-more";
          var a = document.createElement("a");
          a.href = url.href;
          a.textContent = "Read in full →";
          more.appendChild(a);
          p.content.appendChild(more);
          if (!p.box.classList.contains("pinned")) position(p.box, link);
        },
        function () {
          if (!p.box._removed) p.content.innerHTML = '<p class="popup-loading">Couldn’t load preview.</p>';
        }
      );
    });
  }

  // --- Wikipedia: the article's lead, from Wikipedia's page-summary API ---
  function fetchWiki(lang, title) {
    var key = lang + ":" + title;
    if (!wikiCache[key]) {
      wikiCache[key] = fetch("https://" + lang + ".wikipedia.org/api/rest_v1/page/summary/" +
                             encodeURIComponent(title))
        .then(function (res) {
          if (!res.ok) throw new Error("fetch failed: " + res.status);
          return res.json();
        });
    }
    return wikiCache[key];
  }

  function bindWikiLink(link) {
    var m = /^https?:\/\/([a-z-]+)\.(?:m\.)?wikipedia\.org\/wiki\/([^#?]+)/.exec(link.href);
    if (!m) return;
    var lang = m[1];
    var title = decodeURIComponent(m[2]);

    onHover(link, 180, function () {
      var p = show(link, function () {
        var q = makePopup("Wikipedia");
        q.content.innerHTML = '<p class="popup-loading">Fetching Wikipedia article…</p>';
        q.box.classList.add("wiki-popup");
        return q;
      });
      if (!p) return;
      fetchWiki(lang, title).then(
        function (data) {
          if (p.box._removed) return;
          p.titleEl.textContent = (data.title || title.replace(/_/g, " ")) + " (Wikipedia)";
          var html = "";
          if (data.thumbnail && data.thumbnail.source) {
            html += '<img class="wiki-thumb" alt="" src="' + data.thumbnail.source + '">';
          }
          html += data.extract_html || "<p>" + (data.extract || "") + "</p>";
          html += '<p class="popup-more"><a href="' + link.href + '">Read on Wikipedia →</a></p>';
          fillContent(p, html, true);
          if (!p.box.classList.contains("pinned")) position(p.box, link);
        },
        function () {
          if (!p.box._removed) p.content.innerHTML = '<p class="popup-loading">Couldn’t reach Wikipedia.</p>';
        }
      );
    });
  }

  // --- translations: span.translation follows the foreign text it renders.
  // A toggle button shows it inline; hovering the button previews it. ---
  function addTranslationToggle(tr) {
    var prev = tr.previousElementSibling;
    if (prev && prev.classList.contains("translate-toggle")) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "translate-toggle";
    btn.textContent = "English";
    btn.title = "Show a translation (this edition’s, not Lecky’s)";
    btn.setAttribute("aria-expanded", tr.classList.contains("shown") ? "true" : "false");
    tr.parentNode.insertBefore(btn, tr);
  }

  function bindTranslationPreview(btn) {
    var tr = btn.nextElementSibling;
    if (!tr || !tr.classList.contains("translation")) return;
    onHover(btn, SHOW_DELAY, function () {
      if (tr.classList.contains("shown")) return;
      var p = show(btn, function () { return makePopup("Translation (this edition)"); });
      if (!p) return;
      p.box.classList.add("translation-popup");
      fillContent(p, "<p>" + tr.innerHTML.replace(/^\s*\[|\]\s*$/g, "") + "</p>", false);
      position(p.box, btn);
    });
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest(".translate-toggle");
    if (!btn) return;
    var tr = btn.nextElementSibling;
    if (!tr) return;
    var shown = tr.classList.toggle("shown");
    btn.setAttribute("aria-expanded", shown ? "true" : "false");
    clearShow();
    if (btn._popup) removePopup(btn._popup);
  });

  // Wire up everything inside `root` (the page, or a popup's content).
  // `foreign`: the content came from another page or site, so its footnote
  // markers point at notes that aren't on this page.
  function bindAll(root, foreign) {
    root.querySelectorAll(".translation").forEach(addTranslationToggle);
    if (isTouch) return;
    if (!foreign) root.querySelectorAll("a.footnote-ref").forEach(bindFootnoteRef);
    root.querySelectorAll("a.popup-ref").forEach(bindPopupRef);
    root.querySelectorAll('a[href*="wikipedia.org/wiki/"]').forEach(bindWikiLink);
    root.querySelectorAll(".translate-toggle").forEach(bindTranslationPreview);
  }

  function init() {
    // Touch screens get the translation toggles but no hover popups:
    // tapping a footnote marker jumps to the note, and its ↑ jumps back.
    bindAll(document, false);
    if (isTouch) return;
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      clearShow();
      document.querySelectorAll(".popup").forEach(removePopup);
    });
    document.addEventListener("scroll", function () {
      clearShow();
      trimChain(null);
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

    // Long pages also get a collapsible copy in the text column, for screens
    // too narrow to show the margin one (CSS hides whichever doesn't apply).
    if (headings.length >= 5) {
      var details = document.createElement("details");
      details.className = "inline-toc";
      var summary = document.createElement("summary");
      summary.textContent = "Contents";
      details.appendChild(summary);
      details.appendChild(ol.cloneNode(true));
      content.insertBefore(details, content.firstChild);
    }

    content.insertBefore(toc, content.firstChild);
  }

  // Long pages now get a gwern-style nav#TOC from build.py; this margin TOC is
  // only for shorter pages without one.
  if (document.getElementById("TOC")) return;
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
