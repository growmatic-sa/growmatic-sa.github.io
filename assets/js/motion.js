/* Growmatic — motion.js : reveals, cover parallax, search typewriter */
(function(){
'use strict';
var d=document.documentElement;
function still(){return d.classList.contains('gm-still')||window.matchMedia('(prefers-reduced-motion: reduce)').matches;}

/* intro: remove from DOM once finished */
var intro=document.querySelector('.gm-intro');
if(intro){
  var t=d.classList.contains('gm-intro-on')?2500:0;
  setTimeout(function(){ if(intro.parentNode) intro.parentNode.removeChild(intro); }, t);
}

/* scroll reveal */
var SEL='.sec-head,.svc-card,.why-i,.work,.step,.gm-recommendation,.pain,.feat-i,.pk-i,.faq details,.post-card,.val,.vm>div,.ch,.contact-info,.form-card,.v-service-row,.v-manifest h2,.v-manifest-bottom,.v-tech-copy,.v-tech-art,.cta-band,.v-cta-line,.gm-goals,.kpi,.panel,.split>*,.prose>h2,.prose>blockquote,.pk-note,.marquee';
if(!still() && 'IntersectionObserver' in window){
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('gm-in'); io.unobserve(e.target); } });
  },{threshold:.12,rootMargin:'0px 0px -6% 0px'});
  document.querySelectorAll(SEL).forEach(function(el){
    if(el.closest('.gm-cover,.v-hero,.modal,.site-footer')) return;
    var r=el.getBoundingClientRect();
    if(r.top<window.innerHeight*0.9 && r.bottom>0) return;   // already visible: don't hide
    var i=el.parentElement?Array.prototype.indexOf.call(el.parentElement.children,el):0;
    el.style.transitionDelay=(Math.min(i%6,5)*85)+'ms';
    el.classList.add('gm-rv');
    io.observe(el);
  });
  // safety: reveal everything if something goes wrong
  setTimeout(function(){ document.querySelectorAll('.gm-rv:not(.gm-in)').forEach(function(el){ var r=el.getBoundingClientRect(); if(r.top<window.innerHeight) el.classList.add('gm-in'); }); },4000);
}

/* cover parallax */
var media=document.querySelector('.gm-cover-media');
if(media){
  var ticking=false;
  window.addEventListener('scroll',function(){
    if(ticking||still()) return; ticking=true;
    requestAnimationFrame(function(){
      var y=window.scrollY; if(y<1200) media.style.transform='translate3d(0,'+(y*0.22).toFixed(1)+'px,0)';
      ticking=false;
    });
  },{passive:true});
}

/* search chip typewriter */
var tw=document.querySelector('[data-type]');
if(tw){
  var words; try{ words=JSON.parse(tw.getAttribute('data-type')); }catch(e){ words=[]; }
  if(words.length && !still()){
    var wi=0,ci=0,del=false;
    (function step(){
      var w=words[wi];
      if(!del){ ci++; tw.textContent=w.slice(0,ci); if(ci>=w.length){ del=true; return setTimeout(step,1700);} }
      else { ci--; tw.textContent=w.slice(0,ci); if(ci<=0){ del=false; wi=(wi+1)%words.length; } }
      setTimeout(step, del?35:85);
    })();
  }
}
})();
