// Cloudflare Worker：安全標頭注入
// 功能：攔截所有進入 cx468.com.tw 的請求，在回應中加入安全 HTTP 標頭
// 部署方式：
//   1. Cloudflare Dashboard → Workers & Pages → Create Worker
//   2. 貼上此程式碼並儲存
//   3. 到 Workers & Pages → 您的 Worker → Settings → Triggers
//   4. 新增 Route：cx468.com.tw/* 及 www.cx468.com.tw/*

export default {
  async fetch(request, env, ctx) {
    // 取得原始回應
    const response = await fetch(request)

    // 複製回應並注入安全標頭
    const newHeaders = new Headers(response.headers)

    // 防止點擊劫持（禁止網站被嵌入 iframe）
    newHeaders.set('X-Frame-Options', 'DENY')

    // 防止瀏覽器猜測 MIME 類型
    newHeaders.set('X-Content-Type-Options', 'nosniff')

    // 控制 Referrer 資訊洩漏
    newHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin')

    // 強制 HTTPS（1 年有效期）
    newHeaders.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')

    // 關閉不需要的瀏覽器功能（麥克風、相機、地理位置等）
    newHeaders.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=()')

    // Content Security Policy：允許 Google Analytics、Google Tag Manager
    newHeaders.set(
      'Content-Security-Policy',
      [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https://www.google-analytics.com https://www.googletagmanager.com",
        "connect-src 'self' https://www.google-analytics.com https://analytics.google.com https://region1.google-analytics.com",
        "font-src 'self'",
        "frame-src 'none'",
        "object-src 'none'",
        "base-uri 'self'",
      ].join('; ')
    )

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    })
  }
}
