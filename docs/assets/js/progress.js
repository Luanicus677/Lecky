// "Continue reading": on a chapter page, remember how far the reader has got
// (in this browser only); on the home page and the Rationalism contents, offer
// to take them back there. Storage can be missing or blocked: then nothing
// happens.
(function () {
  var KEY = "lecky-reading-place";
  var root = window.LECKY_ROOT || "";
  var rootPath = new URL(root || "./", location.href).pathname;
  var rel = location.pathname.indexOf(rootPath) === 0 ? location.pathname.slice(rootPath.length) : "";
  if (rel === "") rel = "index.html";

  function load() { try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} }

  var content = document.querySelector("section.content");
  var notes = content && content.querySelector("section.footnotes");
  var isChapter = /^rationalism\/(introduction|vol\d-ch\d)\.html$/.test(rel) && notes;

  function span() {
    var top = content.getBoundingClientRect().top + window.scrollY;
    var end = notes.getBoundingClientRect().top + window.scrollY;
    return [top, Math.max(end - top, 1)];
  }

  if (isChapter) {
    var title = (document.title || "").split(" · ")[0].split(" | ")[0];
    var timer = null;
    var record = function () {
      timer = null;
      var s = span(), y = window.scrollY + window.innerHeight * 0.3;
      var pct = Math.min(1, Math.max(0, (y - s[0]) / s[1]));
      var section = "", heads = content.querySelectorAll("h2[id]");
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].getBoundingClientRect().top < window.innerHeight * 0.3) section = heads[i].textContent.trim();
        else break;
      }
      if (pct < 0.01) return;               // only glanced at the top
      save({ rel: rel, title: title, section: section, pct: pct, t: Date.now() });
    };
    window.addEventListener("scroll", function () { if (!timer) timer = setTimeout(record, 800); }, { passive: true });

    // Back from "Continue reading": go to the saved place, not the top.
    if (location.hash === "#resume") {
      var place = load();
      if (place && place.rel === rel) {
        var go = function () { var s = span(); window.scrollTo(0, s[0] + place.pct * s[1] - window.innerHeight * 0.3); };
        go(); window.addEventListener("load", go);
      }
    }
    return;
  }

  // Home page or contents page: offer to continue.
  if (rel !== "index.html" && rel !== "rationalism/index.html") return;
  var place = load();
  if (!place || !place.rel || place.pct > 0.97) return;
  var p = document.createElement("p");
  p.className = "continue-reading";
  var a = document.createElement("a");
  a.href = root + place.rel + "#resume";
  a.textContent = place.title;
  p.appendChild(document.createTextNode("Continue reading: "));
  p.appendChild(a);
  var where = Math.round(place.pct * 100) + "% through";
  p.appendChild(document.createTextNode((place.section ? ", at “" + place.section + "”" : "") + " (" + where + ") →"));
  var first = content && (content.querySelector(".start-here") || content.firstElementChild);
  if (first) content.insertBefore(p, first);
})();
