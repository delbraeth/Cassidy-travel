/* Shared across pages: Calm mode, Larger text, and the touch-screen "?" */
(function(){
  var root = document.documentElement;
  var store = {
    get: function(k){ try { return localStorage.getItem(k); } catch(e){ return null; } },
    set: function(k,v){ try { localStorage.setItem(k,v); } catch(e){} }
  };
  /* display toggles */
  var reduce = false;
  try { reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch(e){}
  function setFlag(n, on, save){
    if (on) root.setAttribute("data-"+n, ""); else root.removeAttribute("data-"+n);
    document.getElementById("t-"+n).setAttribute("aria-pressed", on ? "true" : "false");
    if (save) store.set("ct-"+n, on ? "1" : "0");
  }
  ["calm","large"].forEach(function(n){
    var s = store.get("ct-"+n);
    setFlag(n, s === null ? (n === "calm" ? reduce : false) : s === "1", false);
    document.getElementById("t-"+n).addEventListener("click", function(){ setFlag(n, !root.hasAttribute("data-"+n), true); });
  });

  /* "?" for touch screens: tap to show what Calm mode does */
  var qBtn = document.getElementById("q-calm"), qWrap = qBtn.parentNode;
  function setTip(open){ qWrap.classList.toggle("open", open); qBtn.setAttribute("aria-expanded", open ? "true" : "false"); }
  qBtn.addEventListener("click", function(e){ e.stopPropagation(); setTip(!qWrap.classList.contains("open")); });
  document.addEventListener("click", function(){ setTip(false); });
  document.addEventListener("keydown", function(e){ if (e.key === "Escape") setTip(false); });

})();
