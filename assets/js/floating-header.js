// floating-header.js — a slim header that appears once the reader has
// scrolled past the page's main title, showing the site mark, page title,
// and (if the viewport is tall enough to have scrolled into one) the
// current <h2> section. Own implementation.
(function () {
  "use strict";

  function init() {
    var h1 = document.querySelector("main.article .page-meta h1");
    var siteMark = document.querySelector(".site-header .site-mark");
    if (!h1 || !siteMark) return;

    var header = document.createElement("div");
    header.id = "floating-header";
    header.innerHTML =
      siteMark.outerHTML +
      '<span class="floating-title"></span>' +
      '<span class="floating-sep">&rsaquo;</span>' +
      '<span class="floating-section"></span>';
    document.body.insertBefore(header, document.body.firstChild);

    var titleEl = header.querySelector(".floating-title");
    var sectionEl = header.querySelector(".floating-section");
    // textContent ignores <br> (no text node there), so "Chapter I<br>On the..."
    // would collapse to "Chapter IOn the..." -- turn <br> into a space first.
    var h1Clone = h1.cloneNode(true);
    h1Clone.querySelectorAll("br").forEach(function (br) {
      br.replaceWith(" ");
    });
    titleEl.textContent = (h1Clone.textContent || "").replace(/\s+/g, " ").trim();

    var sections = Array.prototype.slice.call(
      document.querySelectorAll("main.article .content h2")
    );

    function currentSection() {
      var y = window.scrollY + 80; // a bit below the floating header's own height
      var current = null;
      for (var i = 0; i < sections.length; i++) {
        var top = sections[i].getBoundingClientRect().top + window.scrollY;
        if (top <= y) current = sections[i];
        else break;
      }
      return current;
    }

    var ticking = false;
    function update() {
      ticking = false;
      var pastTitle = h1.getBoundingClientRect().bottom < 0;
      header.classList.toggle("visible", pastTitle);

      var sec = currentSection();
      if (sec) {
        sectionEl.textContent = sec.textContent.trim();
        sectionEl.style.display = "";
      } else {
        sectionEl.style.display = "none";
      }
    }

    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(update);
      },
      { passive: true }
    );

    update();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
