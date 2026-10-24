// sidenotes.js — gwern.net-style sidenotes. On screens wide enough to have a
// usable left margin, each footnote is also shown in that margin, level with
// the line that cites it (pushed down when notes would overlap). Narrower
// screens keep the footnote popups and the notes section at the end.
// Must load before popups.js, so the copies are made before popups.js adds
// its translation toggles (it then wires up both copies). Own implementation.
(function () {
  "use strict";

  var content = document.querySelector("main.article .content");
  var notes = content && content.querySelector("section.footnotes");
  if (!notes) return;

  var refs = Array.prototype.slice.call(
    content.querySelectorAll("a.footnote-ref")
  ).filter(function (a) { return !notes.contains(a); });
  if (!refs.length) return;

  var GAP = 28;        // between the margin column and the text
  var MIN_WIDTH = 200; // narrower than this, sidenotes are off
  var MAX_WIDTH = 320;
  var SPACING = 10;    // minimum vertical gap between two sidenotes

  var column = document.createElement("div");
  column.className = "sidenote-column";
  column.setAttribute("aria-hidden", "true"); // the notes section stays the accessible copy

  var pairs = [];
  refs.forEach(function (ref) {
    var note = document.getElementById((ref.getAttribute("href") || "").slice(1));
    if (!note) return;
    var side = document.createElement("div");
    side.className = "sidenote";
    var num = document.createElement("a");
    num.className = "sidenote-num";
    num.href = "#" + ref.id;
    num.textContent = ref.textContent.trim();
    side.appendChild(num);
    var body = note.cloneNode(true);
    body.removeAttribute("id");
    body.querySelectorAll(".footnote-back").forEach(function (el) { el.remove(); });
    body.querySelectorAll("[id]").forEach(function (el) { el.removeAttribute("id"); });
    var inner = document.createElement("div");
    inner.className = "sidenote-body";
    inner.innerHTML = body.innerHTML;
    side.appendChild(inner);
    column.appendChild(side);
    pairs.push({ ref: ref, side: side });

    function hl(on) {
      side.classList.toggle("highlighted", on);
      ref.classList.toggle("highlighted", on);
    }
    [ref, side].forEach(function (el) {
      el.addEventListener("mouseenter", function () { hl(true); });
      el.addEventListener("mouseleave", function () { hl(false); });
    });
  });
  content.appendChild(column);

  var root = document.documentElement;

  function layout() {
    var cRect = content.getBoundingClientRect();
    var width = Math.min(MAX_WIDTH, Math.floor(cRect.left - GAP - 16));
    var on = width >= MIN_WIDTH;
    root.classList.toggle("sidenotes-on", on);
    if (!on) return;
    column.style.width = width + "px";
    column.style.left = -(width + GAP) + "px";
    var bottom = -Infinity;
    pairs.forEach(function (p) {
      var want = p.ref.getBoundingClientRect().top - cRect.top - 4;
      var top = Math.max(want, bottom + SPACING);
      p.side.style.top = top + "px";
      bottom = top + p.side.offsetHeight;
    });
  }

  var pending = null;
  function schedule() {
    if (pending) return;
    pending = requestAnimationFrame(function () { pending = null; layout(); });
  }

  layout();
  window.addEventListener("load", schedule);
  window.addEventListener("resize", schedule);
  if ("ResizeObserver" in window) {
    // images loading, translations opened, fonts swapping: anything that
    // moves the text also moves the markers
    new ResizeObserver(schedule).observe(content);
  }
})();
