#!/usr/bin/env node
'use strict';

/*
 * Behavioural regression tests for the September 2026 site audit.
 * Run from the repository root with: node scripts/audit-regression.cjs
 * Dependency: linkedom@0.18.12. All network, analytics and timers are stubbed.
 * These are DOM/unit checks; they do not claim browser, backend or GSC coverage.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { parseHTML } = require('linkedom');
const ROOT = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(ROOT, name), 'utf8');
const cases = [];
function test(name, run) { cases.push({ name, run }); }
function scripts(html) {
  const { document } = parseHTML(html);
  return [...document.querySelectorAll('script')].map(s => ({
    type: (s.getAttribute('type') || '').toLowerCase(),
    src: s.getAttribute('src'),
    code: s.textContent
  }));
}
function selectScript(file, predicate) {
  const matches = scripts(read(file)).filter(s => !s.src && predicate(s.code));
  assert.equal(matches.length, 1, 'Expected one actual script in ' + file);
  return matches[0].code;
}
function storage(initial) {
  const entries = new Map(Object.entries(initial || {}));
  return {
    getItem: key => entries.has(key) ? entries.get(key) : null,
    setItem: (key, value) => entries.set(key, String(value)),
    removeItem: key => entries.delete(key),
    clear: () => entries.clear(),
    snapshot: () => Object.fromEntries(entries)
  };
}
function environment(html, options = {}) {
  const dom = parseHTML(html);
  const document = dom.document;
  const timers = new Map();
  let clock = 0, nextTimer = 1;
  const requests = [], analytics = [], forwarded = [];
  const location = new URL(options.url || 'https://cx468.com.tw/');
  const localStorage = storage(options.storage);
  const sessionStorage = storage();
  const listeners = new Map();
  class FakeFormData {
    constructor(form) {
      this.entriesList = [];
      if (form) [...form.querySelectorAll('[name]')].forEach(el => {
        if (['checkbox', 'radio'].includes(el.type) && !el.checked) return;
        this.append(el.name, el.value || '');
      });
    }
    append(name, value) { this.entriesList.push([name, value]); }
    get(name) { return (this.entriesList.find(x => x[0] === name) || [])[1] || null; }
    entries() { return this.entriesList[Symbol.iterator](); }
  }
  const sandbox = {
    console, document, location, localStorage, sessionStorage,
    URL, URLSearchParams, Promise, Date, Math, JSON, Number, String, Array, Object,
    Boolean, Error, TypeError, RegExp, Set, Map, parseInt, parseFloat, isNaN,
    encodeURIComponent, decodeURIComponent, FormData: FakeFormData,
    Event: dom.window.Event, CustomEvent: dom.window.CustomEvent,
    innerWidth: options.width || 390, innerHeight: 844, scrollY: 125,
    history: { replaceState(_state, _title, next) { location.href = String(next); } },
    navigator: {},
    getComputedStyle: el => ({ overflow: el.style.overflow || '', display: 'block' }),
    matchMedia: query => ({ get matches() {
      if (/prefers-reduced-motion/.test(query)) return true;
      const min = query.match(/min-width:\s*(\d+)px/), max = query.match(/max-width:\s*(\d+)px/);
      return (!min || sandbox.innerWidth >= Number(min[1])) && (!max || sandbox.innerWidth <= Number(max[1]));
    }, media: query, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }),
    setTimeout(fn, delay = 0) {
      const id = nextTimer++;
      timers.set(id, { fn, at: clock + Number(delay) });
      return id;
    },
    clearTimeout(id) { timers.delete(id); },
    setInterval() { return nextTimer++; }, clearInterval() {},
    requestAnimationFrame(fn) { return sandbox.setTimeout(fn, 16); },
    cancelAnimationFrame(id) { sandbox.clearTimeout(id); },
    requestIdleCallback(fn) { return sandbox.setTimeout(fn, 1); },
    cancelIdleCallback(id) { sandbox.clearTimeout(id); },
    addEventListener(type, fn) {
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(fn);
    },
    removeEventListener(type, fn) {
      listeners.set(type, (listeners.get(type) || []).filter(x => x !== fn));
    },
    scrollTo(_x, y) { sandbox.scrollY = Number(y) || 0; },
    gtag(...args) { analytics.push(args); },
    fbq(...args) { analytics.push(['fbq', ...args]); },
    cxAskFull(q) { forwarded.push(q); },
    fetch(url, init) {
      requests.push({ url: String(url), init });
      if (!options.fetch) return Promise.reject(new Error('Unexpected stubbed fetch: ' + url));
      return Promise.resolve(options.fetch(String(url), init));
    }
  };
  sandbox.window = sandbox;
  sandbox.self = sandbox;
  sandbox.globalThis = sandbox;
  // Linkedom has no browser layout, validity UI or focus manager.
  let active = document.body;
  Object.defineProperty(document, 'activeElement', { configurable: true, get: () => active });
  dom.window.HTMLElement.prototype.focus = function () { active = this; };
  dom.window.HTMLElement.prototype.scrollIntoView = function () {};
  dom.window.HTMLElement.prototype.getBoundingClientRect = function () {
    return { width: 390, height: 58, top: 0, bottom: 58, left: 0, right: 390 };
  };
  [...document.querySelectorAll('form')].forEach(form => {
    form.checkValidity = () => true;
    form.reportValidity = () => true;
    const defaults = [...form.querySelectorAll('input, textarea')].map(el => ({
      el, value: el.tagName === 'TEXTAREA' ? el.textContent : (el.getAttribute('value') || ''),
      checked: el.hasAttribute('checked')
    }));
    form.reset = () => {
      defaults.forEach(item => {
        item.el.value = item.value;
        if (['checkbox', 'radio'].includes(item.el.type)) item.el.checked = item.checked;
      });
    };
  });
  const context = vm.createContext(sandbox);
  function run(code, file = 'site-script') {
    return new vm.Script(code, { filename: file }).runInContext(context, { timeout: 1000 });
  }
  function dispatch(el, type, fields = {}) {
    assert.ok(el, 'Missing target for ' + type);
    const event = new dom.window.Event(type, { bubbles: true, cancelable: true });
    Object.keys(fields).forEach(key => Object.defineProperty(event, key, { value: fields[key] }));
    el.dispatchEvent(event);
    return event;
  }
  function click(el) {
    assert.ok(el, 'Missing click target');
    if (el.disabled) return;
    // A browser runs inline handlers too; linkedom intentionally does not.
    const handler = el.getAttribute('onclick');
    if (handler) run('(function(event){' + handler + '\n}).call(undefined, {})', 'inline-onclick');
    dispatch(el, 'click');
  }
  function tick(ms = 200) {
    const until = clock + ms;
    let count = 0;
    while (true) {
      const due = [...timers.entries()].filter(([, t]) => t.at <= until)
        .sort((a, b) => a[1].at - b[1].at || a[0] - b[0])[0];
      if (!due) break;
      assert.ok(++count < 200, 'Timer loop did not settle');
      timers.delete(due[0]); clock = due[1].at; due[1].fn();
    }
    clock = until;
  }
  return {
    document, sandbox, context, localStorage, requests, analytics, forwarded,
    run, dispatch, click, tick,
    emitWindow(type) { (listeners.get(type) || []).slice().forEach(fn => fn({ type })); },
    events() { return [...analytics, ...(sandbox.dataLayer || []).map(x => [...x])]; }
  };
}
async function flush() { for (let i = 0; i < 20; i++) await Promise.resolve(); }
function q(env, selector) { return env.document.querySelector(selector); }
function initIntake(options = {}) {
  const env = environment(read('intake.html'), {
    url: 'https://cx468.com.tw/intake.html', ...options
  });
  env.run(selectScript('intake.html', code => code.includes('FLOW_COMMON') && code.includes('cx_intake_v1')), 'intake.html');
  return env;
}
function state(env) { return JSON.parse(env.localStorage.getItem('cx_intake_v1') || '{}'); }
function visible(env, selector) { assert.equal(q(env, selector).hidden, false, selector + ' must be visible'); }
function webFormFetch(url) {
  if (url.endsWith('/lead')) return { ok: false, status: 500 };
  if (url.endsWith('/lead-fail')) return { ok: true, status: 200 };
  if (url === 'https://api.web3forms.com/submit') return { ok: true, status: 200, json: async () => ({ success: true }) };
  throw new Error('Unexpected fetch target: ' + url);
}

test('All HTML inline JavaScript and JSON-LD parse', () => {
  let htmlCount = 0, jsCount = 0, jsonCount = 0;
  const skipped = new Set();
  function visit(dir) {
    fs.readdirSync(dir, { withFileTypes: true }).forEach(entry => {
      if (['.git', 'node_modules'].includes(entry.name)) return;
      const file = path.join(dir, entry.name);
      if (entry.isDirectory()) return visit(file);
      if (!entry.name.endsWith('.html')) return;
      htmlCount++;
      scripts(fs.readFileSync(file, 'utf8')).forEach((s, index) => {
        if (s.src) return;
        const label = path.relative(ROOT, file) + ':script-' + (index + 1);
        if (s.type === 'application/ld+json') {
          assert.doesNotThrow(() => JSON.parse(s.code), label); jsonCount++;
        } else if (!s.type || /^(text|application)\/(java|ecma)script$/.test(s.type)) {
          assert.doesNotThrow(() => new vm.Script(s.code, { filename: label }), label); jsCount++;
        } else skipped.add(s.type);
      });
    });
  }
  visit(ROOT);
  assert.ok(htmlCount > 100 && jsCount > 100 && jsonCount > 100, 'Expected a full-site scan');
  new vm.Script(read('nav.js'), { filename: 'nav.js' });
  new vm.Script(read('include.js'), { filename: 'include.js' });
  console.log('  Scanned ' + htmlCount + ' HTML, ' + jsCount + ' inline JS, ' + jsonCount + ' JSON-LD; excluded types: ' + ([...skipped].join(', ') || 'none'));
});

test('Mobile menu Escape restores scroll, icon and ARIA; desktop resize closes it', () => {
  const env = environment('<!doctype html><html><head></head><body><div id="nav"></div></body></html>');
  env.document.body.style.overflow = 'scroll';
  env.run(read('nav.js'), 'nav.js');
  const burger = q(env, '.cx-burger'), sheet = q(env, '#cxSheet');
  const closedIcon = burger.textContent;
  env.click(burger);
  assert.equal(env.document.body.style.overflow, 'hidden');
  assert.equal(burger.getAttribute('aria-expanded'), 'true');
  env.dispatch(env.document, 'keydown', { key: 'Escape' });
  assert.equal(sheet.classList.contains('open'), false);
  assert.equal(burger.getAttribute('aria-expanded'), 'false');
  assert.equal(burger.textContent, closedIcon);
  assert.equal(env.document.body.style.overflow, 'scroll');
  env.click(burger);
  env.sandbox.innerWidth = 1200; env.emitWindow('resize');
  assert.equal(sheet.classList.contains('open'), false, 'Desktop must not retain the mobile overlay');
  assert.equal(env.document.body.style.overflow, 'scroll');
});

test('Expired or legacy intake data is not resumed by navigation or intake', () => {
  for (const saved of [
    { topic: 'leaseback', stepName: 'lead', address: '舊地址不可恢復' },
    { topic: 'leaseback', stepName: 'lead', address: '舊地址不可恢復', updatedAt: Date.now() - 48 * 60 * 60 * 1000 }
  ]) {
    const initial = { cx_intake_v1: JSON.stringify(saved) };
    const nav = environment('<!doctype html><html><head></head><body><div id="nav"></div></body></html>', { storage: initial });
    nav.run(read('nav.js'), 'nav.js');
    assert.equal(q(nav, '#cxResume').hidden, true);
    const intake = initIntake({ storage: initial });
    visible(intake, '#s0');
    assert.notEqual(state(intake).address, saved.address);
    assert.equal(q(intake, '#addr').value || '', '');
  }
});

test('Intake double clicks cannot skip the required address or a choice step', () => {
  const env = initIntake();
  env.click(q(env, '[data-topic="leaseback"]'));
  const stage = q(env, '#s1opts .opt');
  env.click(stage); env.click(stage); env.tick();
  visible(env, '#s2');
  assert.equal(q(env, '#sq').hidden, true);
  assert.equal(q(env, '#next').disabled, true);
  const addr = q(env, '#addr');
  addr.value = '新北市中和區中正路468號';
  env.dispatch(addr, 'input'); env.click(q(env, '#next'));
  visible(env, '#sq');
  assert.equal(state(env).stepName, 'use');
  const choice = q(env, '#sqopts .opt');
  env.click(choice); env.click(choice); env.tick();
  assert.equal(state(env).stepName, 'type');
});

test('Intake Back cancels pending automatic advance', () => {
  const env = initIntake();
  env.click(q(env, '[data-topic="leaseback"]'));
  env.click(q(env, '#s1opts .opt'));
  env.click(q(env, '#back'));
  env.tick(500);
  visible(env, '#s0');
  assert.equal(state(env).stepName || 'topic', 'topic');
});

test('Clear progress removes saved address and input values', () => {
  const env = initIntake();
  env.click(q(env, '[data-topic="leaseback"]'));
  env.click(q(env, '#s1opts .opt')); env.tick();
  const addr = q(env, '#addr');
  addr.value = '新北市中和區中正路468號';
  env.dispatch(addr, 'input');
  q(env, '#fName').value = '測試訪客';
  q(env, '#fPhone').value = '0937051846';
  env.click(q(env, '#clearProgress'));
  assert.equal(env.localStorage.getItem('cx_intake_v1'), null);
  assert.equal(q(env, '#addr').value || '', '');
  assert.equal(q(env, '#fName').value || '', '');
  assert.equal(q(env, '#fPhone').value || '', '');
});

test('Intake ignores duplicate submit, records HTTP notification failure, and clears successful progress', async () => {
  const env = initIntake({ fetch: webFormFetch });
  env.click(q(env, '[data-topic="financing"]'));
  q(env, '#fName').value = '測試訪客';
  q(env, '#fPhone').value = '0937051846';
  q(env, '#consent').checked = true;
  env.dispatch(q(env, '#leadForm'), 'submit');
  env.dispatch(q(env, '#leadForm'), 'submit');
  await flush();
  assert.equal(env.requests.filter(r => r.url.endsWith('/lead')).length, 1);
  assert.equal(env.requests.filter(r => r.url.endsWith('/lead-fail')).length, 1);
  assert.equal(env.requests.filter(r => r.url.includes('api.web3forms.com')).length, 1);
  visible(env, '#s4');
  assert.equal(env.localStorage.getItem('cx_intake_v1'), null);
  const failure = env.requests.find(r => r.url.endsWith('/lead-fail'));
  assert.ok(!String(failure.init.body).includes('0937051846'), 'Failure telemetry must not contain lead values');
});


test('Pending intake submission blocks Back, clear and resubmit until the same request succeeds', async () => {
  let completeSubmission;
  const env = initIntake({
    fetch(url) {
      if (url.endsWith('/lead')) return { ok: true, status: 200 };
      if (url === 'https://api.web3forms.com/submit') {
        return new Promise(resolve => { completeSubmission = resolve; });
      }
      throw new Error('Unexpected fetch target: ' + url);
    }
  });
  env.click(q(env, '[data-topic="financing"]'));
  q(env, '#fName').value = '測試訪客';
  q(env, '#fPhone').value = '0937051846';
  q(env, '#consent').checked = true;
  env.dispatch(q(env, '#leadForm'), 'submit');
  await flush();
  assert.equal(typeof completeSubmission, 'function', 'Web3Forms must still be pending');
  const pendingDraft = env.localStorage.getItem('cx_intake_v1');
  assert.ok(pendingDraft, 'Pending draft must exist until success');
  env.click(q(env, '#back'));
  env.click(q(env, '#clearProgress'));
  env.tick(500);
  visible(env, '#s3');
  assert.equal(state(env).stepName, 'lead', 'Pending submission must stay on the lead step');
  assert.equal(env.localStorage.getItem('cx_intake_v1'), pendingDraft, 'Back/clear must not erase or replace pending draft');
  assert.equal(q(env, '#fName').value, '測試訪客');
  assert.equal(q(env, '#fPhone').value, '0937051846');
  env.dispatch(q(env, '#leadForm'), 'submit');
  await flush();
  assert.equal(env.requests.filter(r => r.url.endsWith('/lead')).length, 1);
  assert.equal(env.requests.filter(r => r.url.includes('api.web3forms.com')).length, 1);
  assert.equal(q(env, '#s4').hidden, true, 'Success must not appear before the response arrives');
  completeSubmission({ ok: true, status: 200, json: async () => ({ success: true }) });
  await flush();
  visible(env, '#s4');
  assert.equal(env.localStorage.getItem('cx_intake_v1'), null);
});

test('Shared lead form isolates notification HTTP failure and prevents duplicate submissions', async () => {
  const env = environment('<!doctype html><html><head></head><body>' + read('lead-form.html') + '</body></html>', { fetch: webFormFetch });
  env.run(selectScript('lead-form.html', code => code.includes('evalForm')), 'lead-form.html');
  q(env, '#consent').checked = true;
  env.dispatch(q(env, '#evalForm'), 'submit');
  env.dispatch(q(env, '#evalForm'), 'submit');
  await flush();
  assert.equal(env.requests.filter(r => r.url.endsWith('/lead')).length, 1);
  assert.equal(env.requests.filter(r => r.url.endsWith('/lead-fail')).length, 1);
  assert.equal(env.requests.filter(r => r.url.includes('api.web3forms.com')).length, 1);
  assert.equal(q(env, '#evalForm').style.display, 'none');
  assert.ok(q(env, '#formMsg').classList.contains('ok'));
});

test('Each homepage or shared-footer sticky CTA click records one analytics event', () => {
  const analytics = read('consultation-tracking.js');
  for (const file of ['index.html', 'footer.html']) {
    const env = environment(file === 'index.html' ? read(file) : '<!doctype html><html><head></head><body>' + read(file) + '</body></html>');
    env.run(analytics, 'delegated-analytics');
    env.run(analytics, 'duplicate-load');
    for (const [selector, eventName] of [['.cx-sticky-line', 'line_click'], ['.cx-sticky-tel', 'phone_click']]) {
      const before = env.events().filter(e => e[0] === 'event' && e[1] === eventName).length;
      env.click(q(env, selector));
      const after = env.events().filter(e => e[0] === 'event' && e[1] === eventName).length;
      assert.equal(after - before, 1, file + ' ' + selector + ' must fire exactly once');
    }
  }
});

test('Consultation tracking uses one event with fixed attribution and no visitor content', () => {
  const files = ['index.html','private-to-bank.html','second-mortgage.html','services.html','debt-consolidation.html','corporate-loan.html','article-private-loan-to-bank.html','article-self-employed-loan.html','article-second-mortgage-scam.html'];
  for (const file of files) {
    const env = environment(read(file), { url: 'https://cx468.com.tw/' + file + '?phone=PRIVATE&debt=PRIVATE' });
    // Execute the real GA bootstrap as well as all contact tracking scripts.
    for (const s of scripts(read(file))) {
      if (!s.src && s.code.includes('function gtag()')) env.run(s.code);
    }
    env.run(read('consultation-tracking.js'));
    env.run(read('consultation-tracking.js'));
    const a = q(env, '.cx-call-primary');
    env.click(a);
    const events = env.events().filter(e => e[0] === 'event' && e[1] === 'phone_click');
    assert.equal(events.length, 1, file);
    assert.deepEqual(Object.keys(events[0][2]).sort(), ['consultation_need','link_location','page_path']);
    assert.ok(!JSON.stringify(events).includes('PRIVATE'));
    assert.equal(events[0][2].link_location, file.startsWith('article-') && file !== 'article-self-employed-loan.html' ? 'article_bottom' : 'hero');
    const expected = file === 'debt-consolidation.html' ? 'private_debt' : file.includes('private') ? 'private_to_bank' : file.includes('second') ? 'second_mortgage' : /corporate|self-employed/.test(file) ? 'corporate_loan' : 'general';
    assert.equal(events[0][2].consultation_need, expected, file);
    env.click(a);
    assert.equal(env.events().filter(e => e[0] === 'event' && e[1] === 'phone_click').length, 2, 'separate clicks are separate events');
  }
});

test('Homepage forwards visitor question to the assistant without raw text in analytics', () => {
  const env = environment(read('index.html'));
  env.run(selectScript('index.html', code => code.includes('function sendToXiaocheng')), 'homepage-assistant');
  const question = '測試訪客私密內容：我的地址與電話不得送進分析系統';
  q(env, '#ask').value = question;
  env.click(q(env, '#send'));
  assert.deepEqual(env.forwarded, [question]);
  const events = env.events().filter(e => e[0] === 'event' && e[1] === 'hero_ai_ask');
  assert.equal(events.length, 1);
  assert.ok(!JSON.stringify(env.events()).includes(question));
  assert.ok(!events.some(e => e[2] && Object.hasOwn(e[2], 'cw_label')), 'Raw-question cw_label must be removed');
});

test('Corporate uploader renders untrusted filename and response case ID as text', async () => {
  const caseID = '<img src=x onerror=alert(1)>';
  const env = environment(read('corporate-checkup.html'), {
    fetch(url) {
      assert.ok(url.endsWith('/checkup'));
      return { ok: true, json: async () => ({ case_id: caseID, files: 0 }) };
    }
  });
  env.run(selectScript('corporate-checkup.html', code => code.includes("var ENDPOINT=")), 'corporate-checkup.html');
  const filename = '<img src=x onerror=alert(1)>.exe';
  env.dispatch(q(env, '#upBox'), 'drop', { dataTransfer: { files: [{ name: filename, size: 100 }] } });
  assert.ok(q(env, '#upErr').textContent.includes(filename));
  assert.equal(q(env, '#upErr img'), null);
  q(env, '#ckConsent').checked = true;
  env.dispatch(q(env, '#ckForm'), 'submit');
  env.dispatch(q(env, '#ckForm'), 'submit');
  await flush();
  assert.equal(env.requests.length, 1, 'Duplicate corporate submit must be ignored');
  assert.ok(q(env, '#ckMsg').textContent.includes(caseID));
  assert.equal(q(env, '#ckMsg img'), null);
  assert.ok(q(env, '#ckMsg').classList.contains('ok'));
});

test('Shared fragments cannot inject crawler noindex; host and standalone directives survive', async () => {
  assert.match(read('footer.html'), /<meta\s+name=["']robots["']\s+content=["']noindex["']/i);
  const env = environment('<!doctype html><html><head><meta name="robots" content="noindex" id="host-policy"></head><body><div data-include="footer"></div></body></html>', {
    fetch(url) {
      assert.equal(url, 'footer.html');
      return { ok: true, text: async () => '<meta name="ROBOTS" content="noindex"><meta name="googlebot" content="noindex"><meta name=" bingbot " content="noindex"><footer id="loaded-footer">Footer</footer>' };
    }
  });
  env.run(read('include.js'), 'include.js');
  env.dispatch(env.document, 'DOMContentLoaded');
  await flush();
  assert.ok(q(env, '#loaded-footer'));
  assert.equal(q(env, '#host-policy').getAttribute('content'), 'noindex');
  assert.equal(env.document.querySelectorAll('body meta[name]').length, 0);
  assert.equal(env.requests.length, 1, 'Deferred assistant and motion must not invoke external services');
});

test('Expanded contact pages sanitize GA location/referrer and emit once per independent click', () => {
  const files = fs.readdirSync(ROOT).filter(f => f.endsWith('.html') && read(f).includes('src="consultation-tracking.js"'));
  assert.equal(files.length, 18);
  for (const file of files) {
    const html = read(file), env = environment(html.replace('</body>', read('footer.html')+'</body>'), {url:'https://cx468.com.tw/'+file+'?phone=PRIVATE#PRIVATE'});
    Object.defineProperty(env.document, 'referrer', {value:'https://example.com/source?name=PRIVATE#PRIVATE'});
    for (const s of scripts(html)) {
      if (!s.src && s.code.includes('function gtag()')) env.run(s.code);
      assert.ok(s.src || !/gtag\(['"]event['"],\s*['"](?:phone_click|line_click)['"]/.test(s.code), file+' legacy contact handler');
    }
    const configs = env.events().filter(e => e[0] === 'config');
    assert.equal(configs.length, 1, file);
    assert.equal(configs[0][2].page_location, 'https://cx468.com.tw/'+file);
    assert.equal(configs[0][2].page_referrer, 'https://example.com/source');
    env.run(read('consultation-tracking.js')); env.run(read('consultation-tracking.js'));
    const anchor = env.document.querySelector('a[href="tel:0222490517"]');
    assert.ok(anchor, file);
    env.click(anchor); env.click(anchor);
    const events = env.events().filter(e=>e[0]==='event'&&e[1]==='phone_click');
    assert.equal(events.length,2,file);
    assert.ok(!JSON.stringify(env.events()).includes('PRIVATE'), file);
  }
});
test('Confirmed phone allowlist rejects unrelated or decorated numbers; nested click and LINE attribution stay private', () => {
  const allowed = ['tel:0222490517','tel:02-2249-0517','tel:+886222490517','tel:+886-2-2249-0517','tel:+886 2 2249 0517','tel:0931087996','tel:0931-087-996','tel:+886931087996','tel:+886-931-087-996','tel:+886 931 087 996','tel:0958139786','tel:0958-139-786','tel:+886958139786','tel:+886-958-139-786','tel:+886 958 139 786'];
  const rejected = ['tel:165','tel:110','tel:0931087997','tel:0958139787','tel:+886931087996?phone=PRIVATE','tel:0958139786;ext=1','tel:02224905170','tel:0222490517?name=PRIVATE','tel:0222490517;ext=123','tel:+886222490518'];
  const env = environment('<html><body><section data-consultation-need="private_debt" data-link-location="article_bottom"><a id="contact"><span>PRIVATE 財務內容</span></a></section></body></html>', {url:'https://cx468.com.tw/test.html?debt=PRIVATE'});
  env.run(read('consultation-tracking.js')); env.run(read('consultation-tracking.js'));
  const a=q(env,'#contact');
  for (const href of allowed.concat(rejected)) {
    a.setAttribute('href',href); const before=env.events().length;
    env.click(a.querySelector('span')); env.click(a.querySelector('span'));
    assert.equal(env.events().length-before,allowed.includes(href)?2:0,href);
    for (const event of env.events().slice(before)) {
      assert.equal(event[1], 'phone_click');
      assert.deepEqual(Object.keys(event[2]).sort(), ['consultation_need','link_location','page_path']);
      assert.ok(!JSON.stringify(event[2]).includes(href.slice(4)), 'No dialled number in analytics');
    }
  }
  a.setAttribute('href','https://lin.ee/PHIfSoY?name=PRIVATE'); env.click(a);
  const last=env.events().at(-1);
  assert.equal(last[1],'line_click');
  assert.deepEqual(JSON.parse(JSON.stringify(last[2])), {page_path:'/test.html',consultation_need:'private_debt',link_location:'article_bottom'});
  assert.ok(!JSON.stringify(env.events()).includes('PRIVATE'));
});
test('Financial FAQ structured answers match visible answers', () => {
  const normalize = text => text.replace(/\s+/g,'').replace(/[，,]/g,'，');
  for(const file of ['article-inherited-property-loan.html','article-private-loan-to-bank.html','article-self-employed-loan.html','contact.html']) {
    const doc=parseHTML(read(file)).document;
    const faqs=[...doc.querySelectorAll('script[type="application/ld+json"]')].map(s=>JSON.parse(s.textContent)).filter(s=>s['@type']==='FAQPage');
    assert.equal(faqs.length,1,file);
    doc.querySelectorAll('script,style').forEach(n=>n.remove());
    const visible=normalize(doc.body.textContent);
    for(const q of faqs[0].mainEntity) assert.ok(visible.includes(normalize(q.acceptedAnswer.text)), file+' '+q.name);
  }
});

test('Mortgage estimates amortize principal, handle zero interest, and do not claim savings', () => {
 const env=environment(read('mortgage-calculator.html'));
 env.run(selectScript('mortgage-calculator.html', c=>c.includes('function calculate()')));
 q(env,'#amount').value='100';q(env,'#rate').value='3';q(env,'#years').value='10';
 env.run('calculate()');
 const num=id=>Number(q(env,id).textContent.replace(/[^0-9.]/g,''));
 assert.equal(num('#monthly'),9656);assert.equal(num('#interest'),158729);
 q(env,'#rate').value='0';env.run('calculate()');
 assert.equal(num('#monthly'),8333);assert.equal(num('#interest'),0);
 env.run("mode='private';calculate()");
 assert.ok(!q(env,'#savingYearLabel').textContent.includes('每年可省'));
 assert.equal(env.requests.length,0);assert.equal(env.events().length,0);
});

(async () => {
  let failed = 0;
  for (const item of cases) {
    try { await item.run(); console.log('PASS ' + item.name); }
    catch (error) { failed++; console.error('FAIL ' + item.name + '\n' + error.stack); }
  }
  console.log((cases.length - failed) + '/' + cases.length + ' regression groups passed.');
  if (failed) process.exitCode = 1;
})();
