import json,html,re
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
root=Path(__file__).parent
catalog=json.loads((root/'catalog-source.json').read_text());rows=catalog['products']
for p in rows:
 p.setdefault('sport','Padel');p.setdefault('gender','Konur')
 if p['eur'] is not None:p['price']=int((Decimal(str(p['eur']))*Decimal('446.4')).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
 if p['price'] is not None:p['price']=((p['price']+9)//500)*500+490
rows.sort(key=lambda p:(p['price'] is None,p['price'] or 0,p['name'],p['color']))
esc=lambda t:html.escape(str(t),quote=True)
cards=[]
for p in rows:
 title=p['name']+' — '+p['color'] if p['color']!='Sjá mynd' else p['name']
 price=f"{p['price']:,}".replace(',','.')+' kr.' if p['price'] is not None else 'Verð væntanlegt'
 button=f'<button class="add" aria-label="Bæta {esc(title)} í körfu">+ Í körfu</button>' if p['price'] is not None else f'<a class="product-inquiry" href="mailto:clubs@clubs.is?subject=Fyrirspurn%20um%20{p["sku"]}">Spyrja um vöru</a>'
 variants=p.get('variants',[]);selector=''
 if len(variants)>1:
  opts=''.join(f'<option value="{i}">{esc(v["color"])}</option>' for i,v in enumerate(variants))
  selector=f'<label class="color-label" for="color-{p["sku"]}">Litur <select class="color-select" id="color-{p["sku"]}" data-variants="{esc(json.dumps(variants,ensure_ascii=False))}">{opts}</select></label>'
 cards.append(f'''<article class="product has-image" data-sport="{p['sport']}" data-gender="{p['gender']}" data-cat="{esc(p['category'])}" data-brand="{p['brand']}" data-sku="{p['sku']}" data-price="{p['price'] or ''}" data-name="{esc(p['name'])}"><div class="product-art"><img src="{esc(p['image'])}" alt="{esc(title)}" loading="lazy" width="600" height="600"></div><div class="product-info"><small>{p['brand']} · {esc(p['category'])}</small><h3>{esc(title)}</h3><p>{esc(p['description'])}</p>{selector}<span class="product-ref">Vörunr. {p['sku']}</span><div class="product-bottom"><b>{price}</b>{button}</div></div></article>''')
filters=''.join(f'<button class="filter{" selected" if c=="Allt" else ""}" type="button" aria-pressed="{str(c=="Allt").lower()}">{c}</button>' for c in ['Allt','Peysur','Bolir','Stuttbuxur','Buxur','Íþróttahaldarar','Skór'])
shop='''<div id="shop" class="view"><section class="shop-hero"><div><div class="eyebrow">CLUBS · Vefverslun</div><h1>FYRIR<br>VÖLLINN.</h1></div><p>Spaðar, fatnaður og skór fyrir leikinn. Veldu íþrótt og vöruflokk.</p></section><div class="shop-sports" aria-label="Íþrótt"><button class="shop-sport selected" data-sport="Padel" aria-pressed="true">PADEL</button><button class="shop-sport" data-sport="Golf" aria-pressed="false">GOLF</button></div><div class="shop-types" aria-label="Vörutegund"><button class="shop-type selected" data-type="clothing" aria-pressed="true">Fatnaður og skór</button><button class="shop-type" data-type="rackets" aria-pressed="false">Padelspaðar</button></div><div class="shop-genders" aria-label="Konur og karlar"><button class="shop-gender selected" data-gender="Konur" aria-pressed="true">Konur</button><button class="shop-gender" data-gender="Karlar" aria-pressed="false">Karlar</button></div><div class="catalog-toolbar"><label for="brandFilter">Vörumerki <select id="brandFilter"><option value="Allt">Öll vörumerki</option><option>Bullpadel</option><option>Nox</option><option>Adidas</option><option>Babolat</option></select></label><span id="productCount" aria-live="polite"></span><span>Lægsta verð fyrst</span></div><div class="filters" aria-label="Vöruflokkar">'''+filters+'</div><p id="catalogEmpty" role="status" hidden></p><section class="products">'+'\n'.join(cards)+'</section></div>'
f=root/'dist/index.html';s=f.read_text();start=s.index('<div id="shop"');end=s.index('</section></div>',start)+len('</section></div>');s=s[:start]+shop+s[end:]
start=s.index('    function filterCatalog()');end=s.index('    const inquiryTopic=',start)
js='''    function filterCatalog(){
      const category=document.querySelector('.filter.selected').textContent,brand=document.querySelector('#brandFilter').value,sport=document.querySelector('.shop-sport.selected').dataset.sport,gender=document.querySelector('.shop-gender.selected').dataset.gender;
      const rackets=document.querySelector('.shop-type.selected').dataset.type==='rackets';
      let count=0;document.querySelectorAll('.product').forEach(p=>{const visible=p.dataset.sport===sport&&(rackets?p.dataset.cat==='Spaðar':p.dataset.cat!=='Spaðar'&&p.dataset.gender===gender)&&(rackets||category==='Allt'||p.dataset.cat===category)&&(brand==='Allt'||p.dataset.brand===brand);p.hidden=!visible;if(visible)count++});
      document.querySelector('#productCount').textContent=count+(count===1?' vara':' vörur');const empty=document.querySelector('#catalogEmpty');empty.hidden=count!==0;empty.textContent=sport==='Golf'?'Golfvörur væntanlegar.':'Engar vörur passa við þessa síun.';
      document.querySelector('#shop .catalog-toolbar').hidden=sport==='Golf';document.querySelector('#shop .filters').hidden=sport==='Golf'||rackets;document.querySelector('.shop-genders').hidden=sport==='Golf'||rackets;document.querySelector('.shop-types').hidden=sport==='Golf';
    }
    function selectCatalogButton(button,group){document.querySelectorAll(group).forEach(x=>{x.classList.toggle('selected',x===button);x.setAttribute('aria-pressed',String(x===button))})}
    document.querySelectorAll('.filter').forEach(f=>f.onclick=()=>{selectCatalogButton(f,'.filter');filterCatalog()});
    document.querySelector('#brandFilter').addEventListener('change',filterCatalog);
    document.querySelectorAll('.shop-sport,.shop-gender,.shop-type').forEach(b=>b.onclick=()=>{selectCatalogButton(b,b.classList.contains('shop-sport')?'.shop-sport':b.classList.contains('shop-type')?'.shop-type':'.shop-gender');document.querySelector('#brandFilter').value='Allt';selectCatalogButton(document.querySelector('.filter'),'.filter');filterCatalog()});
    document.querySelectorAll('.color-select').forEach(select=>select.addEventListener('change',()=>{const variant=JSON.parse(select.dataset.variants)[Number(select.value)],card=select.closest('.product'),title=card.dataset.name+' — '+variant.color;card.querySelector('img').src=variant.imageUrl;card.querySelector('img').alt=title;card.querySelector('h3').textContent=title;card.querySelector('.add')?.setAttribute('aria-label','Bæta '+title+' í körfu')}));filterCatalog();
'''
s=s[:start]+js+s[end:]
css='''<style id="catalog-hierarchy-css">
.shop-types{display:flex;gap:12px;margin-bottom:22px}.shop-type{font:inherit;font-weight:700;padding:12px 18px;border:1px solid #173d29;background:transparent;color:#173d29}.shop-type.selected{background:#173d29;color:white}.shop-genders[hidden],.shop-types[hidden]{display:none}.shop-sports{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:22px}.shop-sport{padding:22px;text-align:left;font:700 24px 'Manrope',sans-serif;letter-spacing:.04em;border:2px solid transparent;background:#e5dfd3;color:#173d29}.shop-sport[data-sport="Padel"].selected{background:#35063e;color:#fff}.shop-sport[data-sport="Golf"].selected{background:#003300;color:#fff}.shop-genders{display:flex;gap:28px;border-bottom:1px solid #c9c9b9;margin-bottom:24px}.shop-gender{background:none;border:0;border-bottom:3px solid transparent;padding:12px 2px;color:#55634f;font-size:18px;font-weight:700}.shop-gender.selected{border-bottom-color:#173d29;color:#173d29}.shop-sport:focus-visible,.shop-gender:focus-visible,.color-select:focus-visible{outline:3px solid #936095;outline-offset:3px}.color-label{font-size:14px;display:flex;align-items:center;gap:12px;margin:0 0 20px;color:#173d29}.color-select{font:inherit;color:#173d29;background:#fff;border:1px solid #b7b9ac;padding:8px;min-width:0;max-width:100%;flex:1}#shop .catalog-toolbar[hidden],#shop .filters[hidden]{display:none}#catalogEmpty{padding:36px 0;font-size:18px;color:#465744}
</style>'''
s=re.sub(r'<style id="catalog-hierarchy-css">.*?</style>','',s,flags=re.S);s=s.replace('</head>',css+'</head>');f.write_text(s);(root/'catalog-source.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2));print(len(rows),'products rendered')
