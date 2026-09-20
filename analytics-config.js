/* Do not copy arbitrary query strings or visitor data into analytics. */
(function () {
  'use strict';
  var config={page_location:location.origin+location.pathname,page_referrer:''};
  try { var ref=new URL(document.referrer); config.page_referrer=ref.origin+ref.pathname; } catch(e) {}
  var qs=new URLSearchParams(location.search);
  var allowed={
    source:['google','google_business_profile','facebook','instagram','threads','youtube','line','embed'],
    medium:['organic','social','paid_social','cpc','referral','email','qr','iframe','paid','leadform','organic_social','channel'],
    campaign:['general','private_debt','private_to_bank','second_mortgage','corporate_loan','inherited','tool-embed','property-management-fees','corp-checkup-202609','home-equity','p2a','meta_one_202609','fanjiuzhang'],
    content:['profile','bio','post','video','menu','website','hero','footer','sticky_bar','article_bottom']
  };
  Object.keys(allowed).forEach(function(key){
    var value=qs.get('utm_'+key);
    if(allowed[key].indexOf(value)!==-1) config[key==='campaign'?'campaign_name':'campaign_'+key]=value;
  });
  // Existing Threads posts use a valid YYMMDD campaign; only that channel may use it.
  var dated=qs.get('utm_campaign')||'';
  if(qs.get('utm_source')==='threads'&&qs.get('utm_medium')==='social'&&/^\d{6}$/.test(dated)){
    var year=2000+Number(dated.slice(0,2)), month=Number(dated.slice(2,4)), day=Number(dated.slice(4,6));
    var date=new Date(Date.UTC(year,month-1,day));
    if(date.getUTCFullYear()===year&&date.getUTCMonth()===month-1&&date.getUTCDate()===day) config.campaign_name=dated;
  }
  window.cxAnalyticsConfig=config;
})();
