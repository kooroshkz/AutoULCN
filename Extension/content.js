// AutoULCN content script
// -----------------------------------------------------------------------------
// Two jobs, both fully self-contained (no popup, no messaging required):
//
//   1. On the MFA *setup* page (account.services.universiteitleiden.nl):
//      detect the revealed TOTP secret and save it as `Secret_Key`.
//
//   2. On the ULCN / MFA *login* pages (login.uaccess / mfa.services):
//      generate the current TOTP from the saved secret and fill it into the
//      code field (#nffc), then click the submit button (#loginButton2) — so
//      you never have to open the extension popup.
//
// TOTP is generated with the browser's built-in Web Crypto API (RFC 6238:
// HMAC-SHA1, 6 digits, 30s period), so no third-party library is needed here.
// -----------------------------------------------------------------------------

// Cross-browser compatibility
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

// ----------------------------------------------------------------------------
// Storage helper (works with both Chrome's callback API and Firefox's promises)
// ----------------------------------------------------------------------------
function storageGet(keys) {
  return new Promise((resolve) => {
    try {
      const maybePromise = browserAPI.storage.local.get(keys, (res) => resolve(res || {}));
      // Firefox returns a promise and ignores the callback.
      if (maybePromise && typeof maybePromise.then === 'function') {
        maybePromise.then((res) => resolve(res || {})).catch(() => resolve({}));
      }
    } catch (e) {
      resolve({});
    }
  });
}

// ----------------------------------------------------------------------------
// TOTP generation (RFC 6238) via Web Crypto
// ----------------------------------------------------------------------------
function base32ToBytes(base32) {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  const cleaned = String(base32).replace(/=+$/, '').replace(/\s+/g, '').toUpperCase();
  let bits = '';
  for (let i = 0; i < cleaned.length; i++) {
    const val = alphabet.indexOf(cleaned[i]);
    if (val === -1) continue; // skip anything that isn't valid Base32
    bits += val.toString(2).padStart(5, '0');
  }
  const bytes = [];
  for (let i = 0; i + 8 <= bits.length; i += 8) {
    bytes.push(parseInt(bits.substring(i, i + 8), 2));
  }
  return new Uint8Array(bytes);
}

async function generateTOTP(secret, { period = 30, digits = 6, timeSec = null } = {}) {
  const key = base32ToBytes(secret);
  if (!key.length) throw new Error('AutoULCN: empty or invalid secret key');

  const epoch = timeSec == null ? Math.floor(Date.now() / 1000) : timeSec;
  const counter = Math.floor(epoch / period);

  // 8-byte big-endian counter. High word covers counters past 2^32 (year ~2106).
  const counterBytes = new ArrayBuffer(8);
  const view = new DataView(counterBytes);
  view.setUint32(0, Math.floor(counter / 0x100000000));
  view.setUint32(4, counter >>> 0);

  const cryptoKey = await crypto.subtle.importKey(
    'raw', key, { name: 'HMAC', hash: 'SHA-1' }, false, ['sign']
  );
  const hmac = new Uint8Array(await crypto.subtle.sign('HMAC', cryptoKey, counterBytes));

  // Dynamic truncation (RFC 4226 §5.3)
  const offset = hmac[hmac.length - 1] & 0x0f;
  const binary =
    ((hmac[offset] & 0x7f) << 24) |
    ((hmac[offset + 1] & 0xff) << 16) |
    ((hmac[offset + 2] & 0xff) << 8) |
    (hmac[offset + 3] & 0xff);

  return (binary % Math.pow(10, digits)).toString().padStart(digits, '0');
}

// ----------------------------------------------------------------------------
// 1) Secret-key detection on the MFA setup page
// ----------------------------------------------------------------------------
function isLikelyBase32Key(s) {
  if (!s || typeof s !== 'string') return false;
  const cleaned = s.replace(/\s+/g, '').toUpperCase();
  return /^[A-Z2-7]{12,64}$/.test(cleaned);
}

function findOtpauthUri() {
  try {
    const html = (document.documentElement && document.documentElement.innerHTML) || '';
    const m = html.match(/otpauth:\/\/totp\/[^\s"'<>\\)]+/i);
    if (m && m[0]) return m[0].replace(/&amp;/g, '&');
  } catch (e) { /* ignore */ }
  return null;
}

function saveSecretKey(secretKey) {
  const cleaned = String(secretKey).replace(/\s+/g, '').trim();
  if (!isLikelyBase32Key(cleaned)) return false;
  const data = { Secret_Key: cleaned };
  const uri = findOtpauthUri();
  if (uri) data.Otpauth_Uri = uri;
  browserAPI.storage.local.set(data, () => {
    showSecretKeyNotification(cleaned);
  });
  return true;
}

function scanForSecret() {
  // Exact element used on the Leiden enroll page, plus a couple of fallbacks.
  const direct = document.querySelector('[data-hidden-value] > .display');
  if (direct && direct.innerText && direct.innerText.trim() !== '••••••••••••••••') {
    if (saveSecretKey(direct.innerText)) return true;
  }
  for (const d of document.querySelectorAll('.display')) {
    const txt = (d.innerText || '').trim();
    if (txt && txt !== '••••••••••••••••' && isLikelyBase32Key(txt)) {
      if (saveSecretKey(txt)) return true;
    }
  }
  return false;
}

function detectAndSaveSecretKey() {
  if (scanForSecret()) return;
  // The secret is revealed asynchronously when the user clicks the eye icon, so
  // watch the page until it appears.
  const observer = new MutationObserver(() => {
    if (scanForSecret()) observer.disconnect();
  });
  const target = document.body || document.documentElement;
  if (target) {
    observer.observe(target, { childList: true, subtree: true, characterData: true });
  }
  const stop = () => observer.disconnect();
  setTimeout(stop, 60000);
  window.addEventListener('beforeunload', stop, { once: true });
}

function showSecretKeyNotification(secretKey) {
  try {
    const notificationDiv = document.createElement('div');
    notificationDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 20px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        z-index: 99999;
        border-radius: 12px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transform: translateX(400px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        max-width: 300px;
        word-wrap: break-word;
    `;

    const icon = document.createElement('span');
    icon.style.cssText = 'display:inline-block;margin-right:8px;font-size:16px;';
    icon.textContent = '🔐';

    const message = document.createElement('span');
    message.innerHTML =
      `<strong>Secret Key Detected!</strong><br>` +
      `<small style="opacity:0.9;">${secretKey.substring(0, 8)}…</small>`;

    notificationDiv.appendChild(icon);
    notificationDiv.appendChild(message);
    document.body.appendChild(notificationDiv);

    requestAnimationFrame(() => { notificationDiv.style.transform = 'translateX(0)'; });
    setTimeout(() => {
      notificationDiv.style.transform = 'translateX(400px)';
      notificationDiv.style.opacity = '0';
      setTimeout(() => { if (notificationDiv.parentNode) notificationDiv.remove(); }, 400);
    }, 4000);
  } catch (e) {
    console.error('AutoULCN: notification error', e);
  }
}

// ----------------------------------------------------------------------------
// 2) Auto-fill the TOTP code on the login / MFA pages
// ----------------------------------------------------------------------------
function setNativeValue(el, value) {
  // Use the native setter so framework-controlled inputs register the change.
  const proto = Object.getPrototypeOf(el);
  const desc = Object.getOwnPropertyDescriptor(el, 'value') ||
               Object.getOwnPropertyDescriptor(proto, 'value');
  if (desc && desc.set) desc.set.call(el, value);
  else el.value = value;
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
}

function findCodeInput() {
  const direct =
    document.querySelector('#nffc') ||
    document.querySelector('input[name="nffc"]') ||
    (isEnrollPage()
      ? (document.querySelector('form[name="Enroll"] input[name="answer"]') ||
         document.querySelector('input[name="answer"]'))
      : null);
  if (direct) return direct;

  if (!location.hostname.includes('mfa.services.universiteitleiden.nl')) return null;

  const candidates = Array.from(document.querySelectorAll(
    'input[autocomplete="one-time-code"], input[inputmode="numeric"], ' +
    'input[type="tel"], input[type="text"], input[type="number"]'
  )).filter((i) => {
    if (i.disabled || i.readOnly || i.type === 'hidden') return false;
    if (i.offsetParent === null) return false; // not visible
    return true;
  });

  // Prefer the standard one-time-code field if present.
  const otc = candidates.find((i) => i.getAttribute('autocomplete') === 'one-time-code');
  if (otc) return otc;

  return candidates.find((i) => {
    const hay = `${i.id} ${i.name} ${i.placeholder} ${i.getAttribute('aria-label') || ''}`.toLowerCase();
    if (/user|email|password|login|account/.test(hay)) return false; // never a credential field
    const maxLen = parseInt(i.getAttribute('maxlength') || '0', 10);
    return (maxLen >= 4 && maxLen <= 8) || /otp|totp|code|token|mfa|2fa|verif/.test(hay);
  }) || null;
}

function findSubmitButton() {
  return document.querySelector('#loginButton2') ||
         document.querySelector('button[type="submit"], input[type="submit"]') ||
         null;
}

let filling = false;   // re-entrancy guard for the async fill
let submitted = false; // ensure we only auto-click submit once per page load

const AUTO_ATTEMPT_KEY = 'autoulcn_auto_attempted';
function hasAutoAttempted() {
  try { return sessionStorage.getItem(AUTO_ATTEMPT_KEY) === '1'; } catch (e) { return false; }
}
function markAutoAttempted() {
  try { sessionStorage.setItem(AUTO_ATTEMPT_KEY, '1'); } catch (e) { /* ignore */ }
}

async function fillCode(isAuto = false) {
  const input = findCodeInput();
  if (!input) return false;
  if (input.dataset.autoulcnFilled) return true; // already handled this element
  if (filling) return false;
  // Auto path only fires once per tab session; manual fills always proceed.
  if (isAuto && hasAutoAttempted()) return false;

  filling = true;
  try {
    const { Secret_Key, Auto_Submit } = await storageGet(['Secret_Key', 'Auto_Submit']);
    if (!Secret_Key) {
      console.warn('AutoULCN: no Secret_Key saved yet — open the extension to add it');
      return false;
    }

    // Avoid filling a code that is about to roll over mid-submit.
    const period = 30;
    const remaining = period - (Math.floor(Date.now() / 1000) % period);
    if (remaining <= 2) {
      await new Promise((r) => setTimeout(r, remaining * 1000 + 250));
    }

    const code = await generateTOTP(Secret_Key, { period });
    setNativeValue(input, code);
    input.dataset.autoulcnFilled = code;
    if (isAuto) markAutoAttempted();
    console.log('AutoULCN: filled the code field');

    if (Auto_Submit === true && !submitted) {
      const btn = findSubmitButton();
      if (btn) {
        submitted = true;
        setTimeout(() => {
          // Only click if we're still on the page and the button is still there.
          if (document.body.contains(btn)) {
            try { btn.click(); } catch (e) {}
          }
        }, 300);
      }
    }
    return true;
  } catch (e) {
    console.error('AutoULCN: fillCode error', e);
    return false;
  } finally {
    filling = false;
  }
}

async function watchForCodeField() {
  // No point watching the page if the user hasn't saved a secret yet.
  const { Secret_Key, Auto_Fill } = await storageGet(['Secret_Key', 'Auto_Fill']);
  if (!Secret_Key) {
    console.log('AutoULCN: no secret saved yet — open the extension to add it. Auto-fill is idle.');
    return;
  }
  if (Auto_Fill !== true) {
    console.log('AutoULCN: auto-fill is off (enable it in the extension settings). Use "Fill Now" to fill manually.');
    return;
  }
  if (hasAutoAttempted()) {
    console.log('AutoULCN: already auto-filled once this session — not retrying automatically. Use "Fill Now" in the popup to retry.');
    return;
  }

  if (await fillCode(true)) return;

  // The MFA page reveals the code field only after a method-selection step,
  // so keep watching the DOM until it appears.
  const observer = new MutationObserver(() => {
    if (hasAutoAttempted()) { observer.disconnect(); return; }
    fillCode(true).then((ok) => { if (ok) observer.disconnect(); });
  });
  const target = document.body || document.documentElement;
  if (target) observer.observe(target, { childList: true, subtree: true });
  const stop = () => observer.disconnect();
  setTimeout(stop, 60000);
  window.addEventListener('beforeunload', stop, { once: true });
}

// Optional manual trigger from the popup ("Fill code now").
browserAPI.runtime.onMessage.addListener((message) => {
  if (message && message.type === 'AUTOULCN_FILL') {
    const input = findCodeInput();
    if (input) delete input.dataset.autoulcnFilled;
    submitted = false;
    fillCode(false);
  }
});

// ----------------------------------------------------------------------------
// Init: decide what to do based on the page we're on.
// ----------------------------------------------------------------------------
function isSetupPage() {
  return location.hostname.includes('account.services.universiteitleiden.nl');
}
function isEnrollPage() {
  return isSetupPage() && location.pathname.includes('/portaal/enroll');
}
function isLoginPage() {
  return location.hostname.includes('login.uaccess.leidenuniv.nl') ||
         location.hostname.includes('mfa.services.universiteitleiden.nl');
}

function init() {
  console.log('AutoULCN: content script loaded on', location.hostname);
  if (isSetupPage()) detectAndSaveSecretKey();
  if (isLoginPage() || isEnrollPage()) watchForCodeField();
}

if (document.readyState === 'complete' || document.readyState === 'interactive') {
  init();
} else {
  document.addEventListener('DOMContentLoaded', init);
}

// Debug helper
try {
  window.AutoULCN = window.AutoULCN || {};
  window.AutoULCN.fillNow = () => fillCode();
  window.AutoULCN.generate = (s) => generateTOTP(s);
} catch (e) { /* ignore */ }
