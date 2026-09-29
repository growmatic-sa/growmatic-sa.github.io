/* Progressive enhancement: content and navigation remain usable without JavaScript. */
(function(){
'use strict';
var script=document.currentScript;
var base=new URL('../../',script.src);
var reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
var paused=reduced.matches;
try{paused=paused||localStorage.getItem('growmatic-motion')==='off';}catch(e){}
var control=document.createElement('button');control.className='gm-motion';control.type='button';
function motion(){document.documentElement.classList.toggle('gm-still',paused);control.textContent=paused?'تشغيل الحركة ◉':'إيقاف الحركة Ⅱ';control.setAttribute('aria-pressed',String(paused));control.setAttribute('aria-label',paused?'تشغيل الحركات التلقائية':'إيقاف الحركات التلقائية');}
control.addEventListener('click',function(){paused=!paused;motion();try{localStorage.setItem('growmatic-motion',paused?'off':'on');}catch(e){}});motion();document.body.appendChild(control);
reduced.addEventListener('change',function(e){paused=e.matches;motion();});
var progress=document.createElement('div');progress.className='gm-progress';progress.setAttribute('aria-hidden','true');document.body.appendChild(progress);
var scheduled=false;function update(){var max=document.documentElement.scrollHeight-innerHeight;progress.style.transform='scaleX('+(max>0?Math.min(scrollY/max,1):0)+')';scheduled=false;}
addEventListener('scroll',function(){if(!scheduled){requestAnimationFrame(update);scheduled=true;}},{passive:true});addEventListener('resize',update);update();
var recommendations={sales:['حملات إعلانية تصل للعميل المناسب','نربط استهداف جمهورك بإعلانات واضحة وصفحات تقنعه بالتواصل، ونتابع الأداء للتحسين.','ads-management'],brand:['حضور رقمي يعبّر عن قيمة علامتك','نرتب رسالتك ومحتواك وقنوات التواصل في استراتيجية واحدة تناسب جمهورك وأهدافك.','digital-marketing'],store:['متجر جاهز لرحلة شراء أسهل','نبني تجربة تسوّق متكاملة من عرض المنتجات إلى الدفع والشحن، على المنصة المناسبة لك.','ecommerce'],systems:['أعمال أوضح وقرارات أسرع','نجمع بيانات الموظفين والحضور والإجازات في لوحات تحكم تسهّل المتابعة اليومية.','hr-dashboards']};
document.querySelectorAll('[data-goal]').forEach(function(button){button.addEventListener('click',function(){var info=recommendations[button.dataset.goal];document.querySelectorAll('[data-goal]').forEach(function(b){b.setAttribute('aria-pressed',String(b===button));});document.getElementById('gm-rec-title').textContent=info[0];document.getElementById('gm-rec-copy').textContent=info[1];document.getElementById('gm-rec-link').href=new URL('services/'+info[2]+'.html',base).href;});});
if('IntersectionObserver' in window){var observer=new IntersectionObserver(function(items){items.forEach(function(item){if(item.isIntersecting){if(!paused)item.target.classList.add('gm-enter');observer.unobserve(item.target);}});},{threshold:.08});document.querySelectorAll('.sec-head,.svc-card,.why-i,.work,.step,.gm-recommendation').forEach(function(el){observer.observe(el);});}
var nav=document.getElementById('nav'),menu=document.getElementById('menuBtn');function closeMenu(){if(nav)nav.classList.remove('open');if(menu)menu.setAttribute('aria-expanded','false');}
if(nav)nav.addEventListener('click',function(e){if(e.target.closest('a, [data-open-booking]'))closeMenu();});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nav&&nav.classList.contains('open')){closeMenu();menu.focus();}});
document.addEventListener('click',function(e){if(nav&&menu&&!nav.contains(e.target)&&!menu.contains(e.target))closeMenu();});
})();
