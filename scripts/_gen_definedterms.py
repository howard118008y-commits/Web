#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""補 definedterm 到高價值頁：各頁『相關且不同』的名詞表(避免mass-template)。
   可見名詞解釋 + DefinedTermSet schema 同源生成。插在 line-qr/footer 前。"""
import json, html, re
esc=lambda x:html.escape(x,quote=True)

TERMS={
"land-value-tax-calculator.html":("地價稅名詞解釋",[
 ("累進起點地價","各縣市以轄區平均地價計算、每兩年公告的金額；土地申報地價總額超過此數，超出部分採累進稅率。"),
 ("申報地價","土地所有權人申報、作為地價稅稅基的地價；未申報者以公告地價 80% 計。"),
 ("自用住宅用地稅率","符合自用條件（設籍、無出租營業、面積上限）的土地，地價稅優惠稅率 2‰。"),
 ("一般用地累進稅率","未達累進起點課 10‰，超過部分按 15‰～55‰ 六級累進。"),
]),
"land-tax-calculator.html":("土地增值稅名詞解釋",[
 ("土地增值稅","土地移轉時，就土地公告現值漲價部分課徵的稅，賣方繳納。"),
 ("漲價總數額","移轉時公告現值減前次移轉現值（經物價指數調整）後的漲價金額，為課稅基礎。"),
 ("自用住宅優惠稅率","符合自用條件可適用 10% 優惠稅率，有「一生一次」與「一生一屋」。"),
 ("重購退稅","出售自用住宅後一定期間內重購、符合條件者，可申請退還已繳土地增值稅。"),
]),
"realestate-tax-calculator.html":("房地合一稅名詞解釋",[
 ("房地合一稅","2016 年起，房屋與土地合併按交易所得課徵的所得稅，依持有期間適用不同稅率。"),
 ("持有期間","自取得至移轉的時間，越短稅率越高（境內個人 2 年內 45%、逐級遞減至 10 年以上 15%）。"),
 ("自住房地優惠","符合自住條件（設籍滿 6 年等），課稅所得 400 萬元以下免稅、超過部分 10%。"),
 ("重購退稅（房地合一）","出售自住房地後重購自住，符合條件可按比例退稅或抵稅。"),
]),
"purchase-cost-calculator.html":("購屋費用名詞解釋",[
 ("契稅","以房屋評定現值為稅基、買賣移轉稅率 6%，由買方繳納。"),
 ("印花稅","不動產買賣契據按金額貼用印花，常見稅率 0.1%。"),
 ("代書費（地政士費）","委託地政士辦理過戶、設定、謄本等的服務費，依案件複雜度而定。"),
 ("履約保證","買賣價金交由第三方（如建經公司）控管、依履約進度撥付，降低交易風險。"),
]),
"vacancy-cost-calculator.html":("空屋成本名詞解釋",[
 ("持有成本","空屋期間仍須支出的費用：房貸利息、管理費、地價稅與房屋稅分攤、保險等。"),
 ("機會成本","空屋未出租而少賺的潛在租金收入，是空置最大的隱形損失。"),
 ("囤房稅","房屋稅對非自住住家用房屋採較高累進稅率（各縣市規定不同），空置且未出租可能適用。"),
]),
"compare-options.html":("不動產資金方案名詞解釋",[
 ("售後回租","屋主將不動產過戶給投資方、同時簽租約繼續居住，並保有日後依約買回權利的資金規劃方式（過戶＋租約＋買回三者一組）。"),
 ("二胎","在既有第一順位房貸之外，再設定第二順位抵押取得資金的貸款，產權不移轉。"),
 ("民間轉銀行","將高利率的民間借款分階段轉回銀行體系，以降低利息負擔。"),
 ("增貸","就名下不動產向原貸款銀行或他行增加貸款額度，產權不移轉。"),
]),
}

def block(title,terms):
    items="".join(
      f'    <div style="border-left:2px solid #d2d2d7;padding:7px 0 7px 16px;margin-bottom:8px">'
      f'<strong style="color:#1d1d1f;font-size:14.5px">{esc(t)}</strong>'
      f'<span style="color:#6e6e73;font-size:13.5px;line-height:1.85"> — {esc(d)}</span></div>\n' for t,d in terms)
    return (f'<section style="max-width:760px;margin:28px auto 0;padding:0 16px">\n'
            f'  <h2 style="font-size:20px;font-weight:700;color:#1d1d1f;margin:0 0 14px">名詞解釋</h2>\n{items}</section>\n')

done=[]
for fn,(tsname,terms) in TERMS.items():
    s=open(fn,encoding="utf-8").read()
    if 'DefinedTerm' in s: print("已有,跳過",fn); continue
    sec=block(tsname,terms)
    if '<div data-include="line-qr"></div>' in s:
        s=s.replace('<div data-include="line-qr"></div>', sec+'<div data-include="line-qr"></div>',1)
    elif '<div data-include="footer"></div>' in s:
        s=s.replace('<div data-include="footer"></div>', sec+'<div data-include="footer"></div>',1)
    else:
        s=s.replace('</body>', sec+'</body>',1)
    sch={"@context":"https://schema.org","@type":"DefinedTermSet","name":tsname,
         "hasDefinedTerm":[{"@type":"DefinedTerm","name":t,"description":d} for t,d in terms]}
    k=s.rfind('</head>'); s=s[:k]+'<script type="application/ld+json">\n'+json.dumps(sch,ensure_ascii=False,indent=1)+'\n</script>\n'+s[k:]
    open(fn,"w",encoding="utf-8").write(s); done.append(fn)
    print(f"✅ {fn}: +{len(terms)}名詞(可見+schema同源)")
print("done",len(done))
