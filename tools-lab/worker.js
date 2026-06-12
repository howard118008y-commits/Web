// ============================================================
// 鋮馨謄本判讀 Cloudflare Worker 後端  worker.js  v0.1
// 職責：收前端送來的「謄本純文字」→ 帶 rules + schema 呼叫 Claude
//       → 回傳符合 schema 的 JSON。金鑰保管在 Worker 環境變數，不外露。
// ============================================================

// ⚠️ 只允許你自己的網域呼叫此端點，防止別人盜用你的 API 額度
const ALLOWED_ORIGINS = [
  "https://cx468.com.tw",
  "https://www.cx468.com.tw",
];

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const corsHeaders = buildCors(origin);

    // 預檢請求
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }
    if (request.method !== "POST") {
      return json({ error: "只接受 POST" }, 405, corsHeaders);
    }
    // 來源檢查
    if (!ALLOWED_ORIGINS.includes(origin)) {
      return json({ error: "來源不允許" }, 403, corsHeaders);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "請求格式錯誤" }, 400, corsHeaders);
    }

    const deedText = (body.deedText || "").trim();
    if (!deedText) {
      return json({ error: "缺少謄本文字" }, 400, corsHeaders);
    }
    // 簡單長度上限，避免異常大請求
    if (deedText.length > 120000) {
      return json({ error: "謄本文字過長" }, 413, corsHeaders);
    }

    // 組系統提示：把規則書 + 輸出格式塞進去
    const systemPrompt = buildSystemPrompt();

    const userPrompt =
      "以下是一份或多份台灣地政電子謄本（含可能的異動索引）的純文字內容，" +
      "請依規則判讀，並嚴格依 schema 輸出單一 JSON 物件，不要附加任何說明文字或 markdown 標記：\n\n" +
      deedText;

    try {
      const resp = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": env.ANTHROPIC_API_KEY,        // ← 金鑰由 Cloudflare 環境變數注入
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model: "claude-opus-4-7",                  // 判讀精度優先；要省成本可改 claude-sonnet-4-6
          max_tokens: 4096,
          system: systemPrompt,
          messages: [{ role: "user", content: userPrompt }],
        }),
      });

      if (!resp.ok) {
        const errText = await resp.text();
        console.log("CLAUDE_ERROR status=" + resp.status + " body=" + errText);
        return json({ error: "Claude API 錯誤", detail: errText }, 502, corsHeaders);
      }

      const data = await resp.json();
      const raw = (data.content || [])
        .filter((b) => b.type === "text")
        .map((b) => b.text)
        .join("\n")
        .trim();

      // 去除可能的 ```json 圍欄後解析
      const cleaned = raw.replace(/^```json\s*/i, "").replace(/```$/i, "").trim();
      let parsed;
      try {
        parsed = JSON.parse(cleaned);
      } catch {
        // 解析失敗時，把原文回給前端方便除錯
        return json({ error: "判讀結果非合法 JSON", raw: cleaned }, 200, corsHeaders);
      }

      return json(parsed, 200, corsHeaders);
    } catch (e) {
      console.log("WORKER_EXCEPTION " + String(e));
      return json({ error: "後端例外", detail: String(e) }, 500, corsHeaders);
    }
  },
};

// ---------- 工具函式 ----------
function buildCors(origin) {
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}

function json(obj, status, extraHeaders) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...extraHeaders },
  });
}

// 把 rules 與 schema 直接寫進系統提示。
// 維護方式：規則有變動 → 同步更新 rules.md 與這裡的 RULES 字串。
// （進階：可改成從 KV 或 R2 讀取，避免兩處維護；MVP 先內嵌。）
function buildSystemPrompt() {
  return `你是鋮馨租賃有限公司的內部謄本判讀助手。一律使用繁體中文。

【鐵則】
1. 依下方規則判讀，並嚴格依下方 schema 輸出單一 JSON 物件。
2. 所有推估數字（反推本金、增值稅、車位坪、估值、LTV）必標 is_estimate:true 並附假設。
3. 此為內部輔助，非正式估價或法律意見；最終決策由承辦人負責。
4. 不確定或謄本未載之處，填 null 並寫入 flags，不得自行腦補。

【規則摘要 rules】
- 債權人六類，依名稱+統編判定：統編8碼純數字=機構(再分 銀行/融資公司/信用合作社/農會漁會/保險公司)；統編英文字母開頭=個人金主。
- 反推本金：機構 ÷1.2；個人金主 ÷1.5~2(少數÷3)，輸出區間。設定金額為共同擔保時不可重複計算。
- 即時試算（坪數，土地與建物【分開處理】，過往最常算錯）：
  ★建物：總建坪=主建物+附屬+公設持分(各筆共有部分總面積×持分,加總)×0.3025，且【不含車位】；車位面積須從公設扣除(找「含停車位編號」那筆的車位持分算出車位面積,從公設減掉)；若無共有部分欄位則公設=0。建物總建坪一律顯示【整間(全棟)】坪數,不可乘持分。另設持分坪=建物總建坪×本人持分比例。
  ★土地：土地是大基地共有,單一住戶只持有極小持分。土地要顯示兩個數字→整筆基地坪=地號總面積×0.3025(此為全社區共有大基地,數字會很大,屬正常)；土地持分坪=地號總面積×本人持分比例×0.3025(此為本人實際持有的土地,通常很小)。【絕對不可把整筆基地總面積當成本人的坪數】。
  ★車位坪獨立計算不計入總建坪,標概估。不算公設比。
  增值稅同時出一般版(20/30/40%)與自用版(10%,假設符合自用資格)，附免責。
- 風險三色燈：紅=查封/假扣押/假處分/破產/普通抵押權清償日已過/設定金額>估值/LTV過高；黃=預告登記/個人金主/買進即套現/異動索引金主走馬燈；綠=純機構無限制無逾期持分完整。
- 跨文件：統編相同=同一人觸發整體鳥瞰；共同擔保多份合併為一案；身分證首碼英文=出生縣市、第一碼數字1男2女，出生地與現居地不符僅供留意。
- 異動索引：依他項權利部新增/刪除重建設定生滅，偵測短期密集設定塗銷(金主走馬燈)，預告登記時間貼合金主設定則佐證，分健康期/惡化期；異動索引揭露之風險高於謄本現況時以較嚴者為準。
- 估值不自建模型，接好時價或實價登錄粗估；合體輸出 LTV=負債/估值、殘值=估值-負債、整體鳥瞰。
- 邊界：限制登記需調卷宗(產生todo)、車位型態查建案、影像版OCR風險先不支援、增值稅精算需補件。

【輸出 schema】
單一 JSON，鍵：case_id, report_date, source_docs, owner{name,id_number,id_birthplace,id_sex,current_address,birthplace_address_match}, parcels[{doc_type,type,id,address,usage,material,floor,build_date,age_years,ownership_scope,acquire_reason,acquire_date,area{total_ping,share_ping,land_total_ping,land_share_ping,parking_ping,parking_present,parking_id,parking_type}(建物用total_ping/share_ping；土地用land_total_ping整筆基地/land_share_ping持分),restrictions[{kind,date,case_number,creditor_or_claimant,scope,needs_court_file}]}], encumbrances[{order,creditor,creditor_id,creditor_class,right_kind,setting_amount,setting_date,maturity_date,clearance_date,is_overdue,principal_estimate,ratio_used,is_estimate,is_common_collateral,common_collateral_targets}], tax_estimate{general_tax,self_use_tax,is_estimate,assumptions[]}, valuation{source,unit_price_ping,total_value,is_estimate}, synthesis{total_debt_estimate,ltv,residual_value,portfolio_view}, history_index{available,timeline_summary,money_lender_carousel,predict_registration_matches_lender,phase}, verdict{light,reasons[],recommendation,todos[]}, flags[]。
只輸出 JSON，不要任何前後文字或 markdown 圍欄。`;
}
