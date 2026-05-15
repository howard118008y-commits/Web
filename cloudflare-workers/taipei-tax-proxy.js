// Cloudflare Worker：台北市地價稅 API 代理
// 功能：代理 services.arpa.tpctax.dof.gov.taipei 的兩支 API，加上 CORS 讓 cx468.com.tw 可直接呼叫
// 部署後 URL 範例：https://taipei-tax-proxy.YOUR-SUBDOMAIN.workers.dev

export default {
  async fetch(request, env, ctx) {

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        }
      })
    }

    const url = new URL(request.url)
    const BASE = 'https://services.arpa.tpctax.dof.gov.taipei/ilCal/'
    const path = url.pathname.replace(/^\/+/, '')

    let targetUrl

    if (path === 'roadname') {
      // 地段查詢：?q=<行政區2碼>  例：?q=01
      const q = url.searchParams.get('q') || ''
      if (!/^\d{2}$/.test(q)) {
        return new Response(JSON.stringify({ error: 'invalid q' }), { status: 400 })
      }
      targetUrl = `${BASE}roadname.php?q=${q}`

    } else if (path === 'search') {
      // 申報地價查詢：?q=<行政區2碼><地段4碼><地號8碼>  例：?q=010600 00250000
      const q = url.searchParams.get('q') || ''
      if (!/^\d{14}$/.test(q)) {
        return new Response(JSON.stringify({ error: 'invalid q' }), { status: 400 })
      }
      targetUrl = `${BASE}search.php?q=${q}`

    } else {
      return new Response('Not found', { status: 404 })
    }

    const upstream = await fetch(targetUrl, {
      headers: {
        'Referer': 'https://services.arpa.tpctax.dof.gov.taipei/ilCal/',
        'Origin': 'https://www.services.tpctax.gov.taipei',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      }
    })

    const text = await upstream.text()

    return new Response(text, {
      headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=86400',  // 地價兩年才改一次，快取 24 小時
      }
    })
  }
}
