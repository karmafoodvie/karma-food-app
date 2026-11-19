#!/usr/bin/env python3
"""Erzeugt kf-icons.js: ersetzt Emojis im Apple-Design zur Laufzeit durch einheitliche SVG-Symbole (Lucide, ISC-Lizenz).
Quelle der Symbole: npm-Paket lucide-static (Pfad als Argument).  python3 test-env/design/gen_icons.py <pfad>/node_modules/lucide-static/icons
Die Emojis bleiben unsichtbar im Text erhalten (textContent unverändert), es wird nur die Anzeige ersetzt."""
import os, re, sys, json
here=os.path.dirname(os.path.abspath(__file__)); src=sys.argv[1]
M={'⚠':['triangle-alert'],'✔':['check'],'✅':['circle-check'],'📦':['package'],'📋':['clipboard-list'],'🔥':['flame'],'❌':['x'],'📅':['calendar'],'🗑':['trash-2'],'🍽':['utensils'],'💬':['message-circle'],'🛒':['shopping-cart'],'✏':['pencil'],'🥗':['salad'],'📍':['map-pin'],'➕':['plus'],'😋':['smile-plus','smile'],'📊':['chart-column','bar-chart-3'],'🔒':['lock'],'📝':['notebook-pen','file-pen-line'],'🎉':['party-popper'],'🔄':['refresh-cw'],'🍛':['soup'],'🆘':['life-buoy'],'💾':['save'],'🧂':['scroll-text'],'🌡':['thermometer'],'ℹ':['info'],'🍰':['cake-slice'],'🥡':['package-open'],'🌶':['flame'],'🚨':['siren'],'🚗':['car'],'↩':['undo-2'],'🚫':['ban'],'👥':['users'],'▶':['play'],'🧹':['brush'],'🥟':['croissant'],'🚚':['truck'],'📖':['book-open'],'🌱':['sprout'],'💶':['euro'],'📈':['trending-up'],'👍':['thumbs-up'],'☀':['sun'],'💯':['badge-check'],'❓':['circle-help','help-circle'],'🗣':['speech','message-square'],'🍲':['soup'],'🧽':['spray-can'],'⏳':['hourglass'],'📱':['smartphone'],'🌙':['moon'],'📤':['upload'],'🏭':['factory'],'📢':['megaphone'],'🙂':['smile'],'🎓':['graduation-cap'],'🌅':['sunrise'],'🥬':['leafy-green'],'🔧':['wrench'],'❄':['snowflake'],'☕':['coffee'],'🗓':['calendar-days'],'🎂':['cake'],'✍':['pen-line'],'🏛':['landmark'],'🤝':['handshake'],'📣':['megaphone'],'💡':['lightbulb'],'🆕':['badge-plus'],'🧊':['snowflake'],'🍚':['soup'],'📸':['camera'],'🔁':['repeat'],'📌':['pin'],'👎':['thumbs-down'],'🚪':['door-open'],'➖':['minus'],'🌐':['globe'],'😖':['frown'],'😐':['meh'],'🤩':['laugh'],'🍖':['drumstick'],'🔗':['link'],'🧪':['flask-conical'],'🎟':['ticket'],'🌬':['wind'],'🚦':['octagon-alert'],'🔎':['search'],'💛':['heart'],'🥕':['carrot'],'🥘':['cooking-pot'],'🎪':['tent'],'📷':['camera'],'🌧':['cloud-rain'],'⛅':['cloud-sun'],'🔍':['search'],'🧯':['fire-extinguisher'],'🩺':['stethoscope'],'⭐':['star'],'📨':['mail'],'🙋':['hand'],'🌿':['leaf'],'🛡':['shield'],'⚡':['zap'],'✨':['sparkles'],'🛍':['shopping-bag'],'🌾':['wheat'],'📞':['phone'],'⚙':['settings'],'🏆':['trophy'],'😴':['bed'],'😃':['laugh'],'🙏':['hand-heart'],'🚛':['truck'],'🧭':['compass'],'🍳':['egg-fried'],'🔀':['shuffle'],'⏰':['alarm-clock'],'🏖':['umbrella'],'🏪':['store'],'📂':['folder-open'],'🗂':['folders'],'👤':['user'],'👈':['arrow-left'],'📄':['file-text'],'☑':['square-check'],'🔔':['bell'],'🎤':['mic'],'🫙':['milk'],'🏃':['footprints'],'🌍':['earth','globe'],'♻':['recycle'],'⚖':['scale'],'💳':['credit-card'],'🎁':['gift'],'👨‍🍳':['chef-hat'],'🥜':['nut'],'🌟':['star'],'🥩':['beef'],'🥣':['soup'],'🥦':['leafy-green'],'🫘':['bean'],'🗺':['map'],'👋':['hand'],'🔑':['key'],'📥':['download'],'⏱':['timer'],'🏢':['building-2'],'🔓':['lock-open'],'🕐':['clock'],'🕘':['clock'],'✉':['mail'],'❤':['heart'],'💰':['coins'],'🪙':['coins'],'📁':['folder'],'🍎':['apple'],'🥛':['milk'],'🥚':['egg'],'🍞':['wheat'],'📚':['library'],'📉':['trending-down'],'🤖':['bot'],'👁':['eye'],'💪':['biceps-flexed'],'⏸':['pause'],'☎':['phone'],'🏷':['tag'],'💧':['droplet'],'💦':['droplets'],'🎯':['target'],'🎵':['music'],'🎨':['palette'],'🧼':['droplets'],'🧴':['spray-can'],'📐':['ruler'],'🍝':['utensils'],'📬':['mailbox'],'🏦':['landmark'],'🥇':['medal'],'🥈':['medal'],'🥉':['medal'],'🅿':['square-parking'],'🏬':['store'],'🐭':['rat'],'🍬':['candy'],'🍋':['citrus'],'🍊':['citrus'],'🍌':['banana'],'🍓':['cherry'],'✋':['hand'],'🧺':['shopping-basket'],'🛵':['bike'],'🎈':['party-popper'],'🥳':['party-popper'],'🎊':['party-popper'],'🫖':['coffee'],'↔':['move-horizontal'],'↗':['arrow-up-right'],'↘':['arrow-down-right'],'🚻':['users'],'🤔':['circle-help','help-circle'],'😊':['smile'],'😍':['heart'],'😕':['frown'],'😔':['frown'],'😬':['meh'],'🤗':['smile'],'🤷':['circle-help','help-circle'],'👏':['thumbs-up'],'👌':['thumbs-up'],'🙌':['party-popper'],'👆':['arrow-up'],'🥱':['bed'],'🫣':['eye-off'],'🧈':['milk'],'🧀':['milk'],'🍯':['droplet'],'🍃':['leaf'],'🌈':['rainbow'],'🫕':['cooking-pot'],'🥙':['sandwich'],'🥫':['package'],'🍶':['milk'],'🫒':['leaf'],'🧄':['leaf'],'🧅':['leaf'],'🫑':['carrot'],'🥒':['carrot'],'🌽':['wheat'],'🍄':['leaf'],'🍅':['apple'],'🥭':['citrus'],'🍍':['citrus'],'🥥':['nut'],'🥔':['carrot'],'🍗':['drumstick'],'🍧':['ice-cream-bowl','ice-cream-cone'],'🍮':['cake-slice']}
DOTS={'🔴':'#D92D20','🟠':'#E8A53A','🟡':'#F5C400','🟢':'#108474','🔵':'#2F6FE4','🟣':'#7C5CC4','⚪':'#C8C8C8','⬜':'#C8C8C8','🟩':'#108474'}
icons={}; emap={}; miss=[]
for emo,cands in M.items():
    name=next((c for c in cands if os.path.exists(os.path.join(src,c+'.svg'))),None)
    if not name: miss.append(emo+':'+cands[0]); continue
    if name not in icons:
        svg=open(os.path.join(src,name+'.svg'),encoding='utf-8').read()
        inner=re.search(r'<svg[^>]*>(.*)</svg>',svg,flags=re.S).group(1)
        icons[name]=re.sub(r'\s+',' ',inner).strip().replace('> <','><')
    emap[emo]=name
js='''<script id="kf-icons">/* GENERIERT von gen_icons.py: Emojis -> einheitliche SVG-Symbole (Lucide, ISC-Lizenz). Nur im Apple-Design; ausschalten mit ?icons=emoji. */
(function(){
  try{var q=location.search.match(/[?&]icons=(svg|emoji)\\b/);if(q)localStorage.setItem('kf_icons',q[1]);}catch(e){}
  var off=false;try{off=localStorage.getItem('kf_icons')==='emoji';}catch(e){}
  if(off||!document.documentElement.classList.contains('apple')) return;
  var I=__ICONS__,E=__EMAP__,D=__DOTS__;
  var RE=/\\p{Extended_Pictographic}(?:\\uFE0F|\\u200D\\p{Extended_Pictographic}|[\\u{1F3FB}-\\u{1F3FF}])*/gu;
  var SKIP={SCRIPT:1,STYLE:1,TEXTAREA:1,OPTION:1,TITLE:1,INPUT:1,SELECT:1};
  function key(m){var k=m.replace(/[\\uFE0F\\u{1F3FB}-\\u{1F3FF}]/gu,'');if(E[k]||D[k])return k;var f=Array.from(k)[0];return (E[f]||D[f])?f:null;}
  function make(k,raw){var s=document.createElement('span');s.className='kf-svg';s.setAttribute('aria-hidden','true');
    s.innerHTML=(D[k]?'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8" fill="'+D[k]+'"/></svg>':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'+I[E[k]]+'</svg>')+'<span class="kf-e"></span>';
    s.lastChild.textContent=raw;return s;}
  function text(n){var p=n.parentNode;if(!p||SKIP[p.nodeName]||(p.classList&&(p.classList.contains('kf-e')||p.classList.contains('kf-svg'))))return;
    if(p.closest&&p.closest('[data-no-svg],#__testbanner,#bday-banner'))return;
    var v=n.nodeValue;if(!v||v.length<1)return;RE.lastIndex=0;var m,last=0,frag=null;
    while((m=RE.exec(v))){var k=key(m[0]);if(!k)continue;if(!frag)frag=document.createDocumentFragment();
      if(m.index>last)frag.appendChild(document.createTextNode(v.slice(last,m.index)));frag.appendChild(make(k,m[0]));last=m.index+m[0].length;}
    if(!frag)return;if(last<v.length)frag.appendChild(document.createTextNode(v.slice(last)));p.replaceChild(frag,n);}
  function walk(root){if(root.nodeType===3){text(root);return;}if(root.nodeType!==1||SKIP[root.nodeName])return;
    var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null),a=[],n;while((n=w.nextNode()))a.push(n);for(var i=0;i<a.length;i++)text(a[i]);}
  function start(){walk(document.body);
    try{new MutationObserver(function(ms){for(var i=0;i<ms.length;i++){var m=ms[i];if(m.type==='characterData'){text(m.target);continue;}for(var j=0;j<m.addedNodes.length;j++)walk(m.addedNodes[j]);}}).observe(document.body,{childList:true,subtree:true,characterData:true});}catch(e){}}
  if(document.body)start();else document.addEventListener('DOMContentLoaded',start);
})();
</script>
'''
js=js.replace('__ICONS__',json.dumps(icons,ensure_ascii=False,separators=(',',':'))).replace('__EMAP__',json.dumps(emap,ensure_ascii=False,separators=(',',':'))).replace('__DOTS__',json.dumps(DOTS,ensure_ascii=False,separators=(',',':')))
open(os.path.join(here,'kf-icons.html'),'w',encoding='utf-8').write(js)
print('Emojis zugeordnet:',len(emap),'| Symbole:',len(icons),'| Größe:',len(js),'| fehlend:',miss)
