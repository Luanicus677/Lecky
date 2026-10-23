// sidenotes.js — positions margin sidenotes to avoid overlapping each
// other, re-running on resize. Progressive enhancement: without this,
// sidenotes.css already places them via plain CSS floats (Tufte-CSS
// technique), which works but can let two close-together notes overlap.
//
// This is our own implementation. The approach -- greedily placing notes
// top-to-bottom, pushing a note down past the previous one's bottom edge
// plus a spacing margin when it would otherwise overlap -- is a
// simplified version of the idea in gwern.net's sidenotes.js (MIT,
// Said Achmiz): https://github.com/gwern/gwern.net/blob/master/build/...
// Their version additionally handles proscribed ranges from images/tables
// intruding into the margin, dual left+right columns, and hash-navigation
// scroll-to-sidenote -- none of which this site currently has a need for.
(function () {
  "use strict";

  var MIN_VIEWPORT_WIDTH = 1180; // keep in sync with the CSS breakpoint
  var SIDENOTE_SPACING = 24; // px, minimum gap between stacked sidenotes

  function viewportWideEnough() {
    return window.innerWidth >= MIN_VIEWPORT_WIDTH;
  }

  function positionSidenotes() {
    var content = document.querySelector("main.article .content");
    if (!content) return;
    var sidenotes = Array.prototype.slice.call(content.querySelectorAll(".sidenote"));
    if (sidenotes.length === 0) return;

    if (!viewportWideEnough()) {
      // Narrow viewport: let the CSS media query's static/inline treatment
      // take over; undo any inline positioning from a previous wide layout.
      sidenotes.forEach(function (sn) {
        sn.classList.remove("js-positioned");
        sn.style.top = "";
      });
      return;
    }

    var contentTop = content.getBoundingClientRect().top + window.scrollY;
    var lastBottom = 0;

    sidenotes.forEach(function (sidenote) {
      var refId = "fnref:" + sidenote.id.replace(/^sn:/, "");
      var citation = document.getElementById(refId);
      if (!citation) return;

      sidenote.classList.add("js-positioned");
      // Measure height with the class already applied (position: absolute
      // changes its box, so float-based height would be wrong).
      var height = sidenote.offsetHeight;

      var citationTop = citation.getBoundingClientRect().top + window.scrollY;
      var targetTop = Math.max(0, citationTop - contentTop);

      var top = Math.max(targetTop, lastBottom === 0 ? targetTop : lastBottom + SIDENOTE_SPACING);
      sidenote.style.top = top + "px";
      lastBottom = top + height;
    });
  }

  var rafQueued = false;
  function scheduleReposition() {
    if (rafQueued) return;
    rafQueued = true;
    requestAnimationFrame(function () {
      rafQueued = false;
      positionSidenotes();
    });
  }

  window.addEventListener("resize", scheduleReposition, { passive: true });
  window.addEventListener("load", scheduleReposition);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleReposition);
  } else {
    scheduleReposition();
  }
})();
