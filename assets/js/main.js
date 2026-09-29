/* Growmatic — main.js (shared by all pages) */

// بريد استقبال الفورمز (FormSubmit)
var FORM_ENDPOINT = "https://formsubmit.co/ajax/tahamahm3@gmail.com";

// شعارات شركاء النجاح (الملفات في /assets/img/partners/)
var PARTNERS = [
  ["شمو للاستثمار","p01"],["SQC","p02"],["عباقر للصناعة والاستثمار","p03"],["مجموعة بن لادن العالمية القابضة","p04"],
  ["جمعية واعي","p05"],["كلين لايف","p06"],["شركة الخليج للتموين","p07"],["بن شيهون","p08"],
  ["مؤسسة إبداع المنزل للمقاولات العامة","p09"],["شريك نجاح","p10"],["شركة برج الحضارة للتجارة","p11"],["شركة أجياد العربية العقارية","p12"],
  ["ريعان للاستشارات الهندسية","p13"],["مجد للتطوير العقاري","p14"],["رموز الخليج للمقاولات","p15"],["شركة درر العواصم للعقارات","p16"],
  ["شركة نبت الاستثمارية العقارية","p17"],["حرفة للمحاماة","p18"],["مستديم","p19"],["أوقاف الشيخ محمد بن عبدالعزيز الراجحي","p20"]
];

window.dataLayer = window.dataLayer || [];
function track(obj){ try { window.dataLayer.push(obj); } catch(e){} }

(function(){
  var y = document.getElementById("year"); if (y) y.textContent = new Date().getFullYear();

  /* ---------- Mobile menu ---------- */
  var menuBtn = document.getElementById("menuBtn"), nav = document.getElementById("nav");
  if (menuBtn && nav){
    menuBtn.addEventListener("click", function(){
      var open = nav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open);
    });
  }

  /* ---------- Partners marquee ---------- */
  var track_ = document.getElementById("partnersTrack");
  if (track_){
    var html = PARTNERS.map(function(p){
      return '<div class="partner"><img src="/assets/img/partners/'+p[1]+'.webp" alt="'+p[0]+'" loading="lazy" width="180" height="80"></div>';
    }).join("");
    track_.innerHTML = html + html.replace(/<div class="partner"><img /g,'<div class="partner" aria-hidden="true"><img ');
  }

  /* ---------- Portfolio filter ---------- */
  var workSeg = document.getElementById("workSeg");
  if (workSeg){
    workSeg.addEventListener("click", function(e){
      var b = e.target.closest("button"); if (!b) return;
      workSeg.querySelectorAll("button").forEach(function(x){ x.setAttribute("aria-pressed", x === b); });
      var f = b.dataset.filter;
      document.querySelectorAll(".work").forEach(function(w){ w.hidden = !(f === "all" || w.dataset.cat === f); });
    });
  }

  /* ---------- Modals ---------- */
  var active = null, lastFocus = null;
  function openModal(m, focusEl){
    if (!m) return;
    lastFocus = document.activeElement;
    if (nav) nav.classList.remove("open");
    m.classList.add("open"); m.setAttribute("aria-hidden","false");
    document.body.style.overflow = "hidden"; active = m;
    setTimeout(function(){ (focusEl || m.querySelector(".modal-close")).focus(); }, 50);
  }
  function closeModal(){
    if (!active) return;
    active.classList.remove("open"); active.setAttribute("aria-hidden","true");
    document.body.style.overflow = ""; active = null;
    if (lastFocus) lastFocus.focus();
  }
  var booking = document.getElementById("bookingModal"), lightbox = document.getElementById("lightbox");
  document.querySelectorAll("[data-open-booking]").forEach(function(b){
    b.addEventListener("click", function(e){ e.preventDefault(); openModal(booking, document.getElementById("b-name")); track({event:"booking_open"}); });
  });
  document.querySelectorAll("[data-close-modal]").forEach(function(b){ b.addEventListener("click", closeModal); });
  document.addEventListener("keydown", function(e){
    if (!active) return;
    if (e.key === "Escape") closeModal();
    if (e.key === "Tab"){
      var f = active.querySelectorAll("button, input:not(.hp), select, textarea");
      var first = f[0], last = f[f.length-1];
      if (e.shiftKey && document.activeElement === first){ e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last){ e.preventDefault(); first.focus(); }
    }
  });
  if (location.hash === "#book") setTimeout(function(){ openModal(booking, document.getElementById("b-name")); }, 300);

  /* ---------- Portfolio designs: scale + lightbox ---------- */
  function fit(shot){
    var inner = shot.querySelector(".shot-inner");
    if (inner && shot.clientWidth) inner.style.transform = "scale(" + (shot.clientWidth / 1280) + ")";
  }
  var shots = document.querySelectorAll(".shot");
  if (shots.length){
    if ("ResizeObserver" in window){
      var ro = new ResizeObserver(function(en){ en.forEach(function(x){ fit(x.target); }); });
      shots.forEach(function(s){ ro.observe(s); });
    } else { shots.forEach(fit); window.addEventListener("resize", function(){ document.querySelectorAll(".shot").forEach(fit); }); }
    var lbShot = document.getElementById("lbShot"), lbTitle = document.getElementById("lbTitle");
    document.querySelectorAll("button.shot").forEach(function(btn){
      btn.addEventListener("click", function(){
        var fig = btn.closest(".work");
        lbTitle.textContent = fig.querySelector("figcaption strong").textContent;
        lbShot.innerHTML = ""; lbShot.appendChild(btn.querySelector(".shot-inner").cloneNode(true));
        openModal(lightbox); requestAnimationFrame(function(){ fit(lbShot); });
        track({event:"portfolio_view", item: lbTitle.textContent});
      });
    });
  }

  /* ---------- Contact click tracking (for GTM conversions) ---------- */
  document.addEventListener("click", function(e){
    var a = e.target.closest("a"); if (!a) return;
    var h = a.getAttribute("href") || "", m = null;
    if (h.indexOf("wa.me") > -1) m = "whatsapp";
    else if (h.indexOf("tel:") === 0) m = "phone";
    else if (h.indexOf("instagram.com") > -1) m = "instagram";
    else if (h.indexOf("tiktok.com") > -1) m = "tiktok";
    if (m) track({event:"contact_click", contact_method:m, page_path:location.pathname});
  });

  /* ---------- Booking date min ---------- */
  var dIn = document.getElementById("b-date");
  if (dIn){ var d = new Date(); dIn.min = d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0"); }

  /* ---------- Forms ---------- */
  function validField(input){
    var v = input.value.trim();
    if (input.required && !v) return false;
    if (!v) return true;
    if (input.type === "email") return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);
    if (input.hasAttribute("data-phone")) return v.replace(/[^\d]/g,"").length >= 9;
    if (input.type === "date" && input.min) return v >= input.min;
    return true;
  }
  function validate(form){
    var ok = true, firstBad = null;
    form.querySelectorAll("input:not(.hp):not([type=hidden]), select").forEach(function(inp){
      var wrap = inp.closest(".field"), good = validField(inp);
      if (wrap) wrap.classList.toggle("invalid", !good);
      if (!good){ ok = false; if (!firstBad) firstBad = inp; }
    });
    if (firstBad) firstBad.focus();
    return ok;
  }
  document.querySelectorAll(".field input, .field select").forEach(function(inp){
    inp.addEventListener("input", function(){
      var w = inp.closest(".field");
      if (w && w.classList.contains("invalid") && validField(inp)) w.classList.remove("invalid");
    });
  });
  document.querySelectorAll("form[data-lead]").forEach(function(form){
    var status = form.querySelector(".status"), btn = form.querySelector("button[type=submit]");
    form.addEventListener("submit", function(e){
      e.preventDefault();
      status.className = "status"; status.textContent = "";
      var hp = form.querySelector(".hp"); if (hp && hp.value) return;
      if (!validate(form)) return;
      var data = {};
      new FormData(form).forEach(function(v,k){ if (k !== "_honey" && String(v).trim()) data[k] = String(v).trim(); });
      data["الصفحة"] = document.title;
      data._subject = form.dataset.subject;
      data._template = "table";
      data._replyto = form.querySelector("input[type=email]").value.trim();
      btn.setAttribute("aria-busy","true");
      var label = btn.textContent; btn.textContent = "جارٍ الإرسال...";
      fetch(FORM_ENDPOINT, { method:"POST", headers:{ "Content-Type":"application/json", "Accept":"application/json" }, body: JSON.stringify(data) })
      .then(function(r){ return r.json(); })
      .then(function(res){
        if (res && (res.success === true || res.success === "true")){
          status.className = "status ok"; status.textContent = form.dataset.success; form.reset();
          track({event:"generate_lead", lead_type: form.dataset.lead, service: data["الخدمة المطلوبة"] || "", page_path: location.pathname});
        } else { throw new Error("failed"); }
      })
      .catch(function(){
        status.className = "status bad";
        status.textContent = "لم يتم الإرسال. تحقق من الاتصال وحاول مرة أخرى، أو راسلنا على واتساب.";
      })
      .finally(function(){ btn.removeAttribute("aria-busy"); btn.textContent = label; });
    });
  });
})();
