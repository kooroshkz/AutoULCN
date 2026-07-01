// Cross-browser compatibility
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

// ---------------------------------------------------------------------------
// TOTP generation (RFC 6238) — the same verified implementation as content.js,
// so the popup display and the auto-fill always agree.
// ---------------------------------------------------------------------------
function base32ToBytes(base32) {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  const cleaned = String(base32).replace(/=+$/, '').replace(/\s+/g, '').toUpperCase();
  let bits = '';
  for (let i = 0; i < cleaned.length; i++) {
    const val = alphabet.indexOf(cleaned[i]);
    if (val === -1) continue;
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
  if (!key.length) throw new Error('empty or invalid secret key');
  const epoch = timeSec == null ? Math.floor(Date.now() / 1000) : timeSec;
  const counter = Math.floor(epoch / period);
  const counterBytes = new ArrayBuffer(8);
  const view = new DataView(counterBytes);
  view.setUint32(0, Math.floor(counter / 0x100000000));
  view.setUint32(4, counter >>> 0);
  const cryptoKey = await crypto.subtle.importKey(
    'raw', key, { name: 'HMAC', hash: 'SHA-1' }, false, ['sign']
  );
  const hmac = new Uint8Array(await crypto.subtle.sign('HMAC', cryptoKey, counterBytes));
  const offset = hmac[hmac.length - 1] & 0x0f;
  const binary =
    ((hmac[offset] & 0x7f) << 24) |
    ((hmac[offset + 1] & 0xff) << 16) |
    ((hmac[offset + 2] & 0xff) << 8) |
    (hmac[offset + 3] & 0xff);
  return (binary % Math.pow(10, digits)).toString().padStart(digits, '0');
}

function isLikelyBase32Key(s) {
  if (!s || typeof s !== 'string') return false;
  return /^[A-Z2-7]{12,64}$/.test(s.replace(/\s+/g, '').toUpperCase());
}

// ---------------------------------------------------------------------------
// UI helpers
// ---------------------------------------------------------------------------
function showElement(element) {
  if (!element) return;
  element.classList.remove('hidden');
  element.style.display = 'block';
}

function hideElement(element) {
  if (!element) return;
  element.classList.add('hidden');
  element.style.display = 'none';
}

function showNotification(message, type = 'success') {
  console.log(`${type.toUpperCase()}: ${message}`);
}

// tabs.sendMessage that works on both Chrome (callback) and Firefox (promise),
// resolving to whether a content script actually received the message.
function sendMessageSafely(tabId, message) {
  return new Promise((resolve) => {
    try {
      const maybePromise = browserAPI.tabs.sendMessage(tabId, message, () => {
        resolve(!browserAPI.runtime.lastError);
      });
      if (maybePromise && typeof maybePromise.then === 'function') {
        maybePromise.then(() => resolve(true)).catch(() => resolve(false));
      }
    } catch (e) {
      resolve(false);
    }
  });
}

browserAPI.tabs.query({ active: true, currentWindow: true }, function (tabs) {
  const currentTab = tabs && tabs[0];
  const currentUrl = (currentTab && currentTab.url) || '';
  const isULCN = currentUrl.startsWith("https://login.uaccess.leidenuniv.nl") ||
                 currentUrl.startsWith("https://mfa.services.universiteitleiden.nl") ||
                 currentUrl.startsWith("https://account.services.universiteitleiden.nl/portaal");

  browserAPI.storage.local.get(['Secret_Key', 'Auto_Fill', 'Auto_Submit', 'Otpauth_Uri'], function (result) {
    const storedSecretKey = result.Secret_Key;
    const storedOtpauthUri = result.Otpauth_Uri;

    const statusElement = document.getElementById("status");
    const secretKeyInputElement = document.getElementById("secretKeyInput");
    const saveButton = document.getElementById("saveButton");
    const totpCodeValueElement = document.getElementById("totpCodeValue");
    const totpLabelElement = document.querySelector(".totp-label");
    const copyButton = document.getElementById("copyButton");
    const totpSection = document.getElementById("totpSection");
    const settingsButton = document.getElementById("settingsButton");
    const settingsLink = document.getElementById("settingsLink");
    const mainPage = document.getElementById("mainPage");
    const settingsPage = document.getElementById("settingsPage");
    const viewSecretButton = document.getElementById("viewSecretButton");
    const resetButton = document.getElementById("resetButton");
    const backButton = document.getElementById("backButton");
    const secretKeyDisplay = document.getElementById("secretKeyDisplay");
    const qrCodeContainer = document.getElementById("qrCodeContainer");
    const qrCodeImg = document.getElementById("qrCodeImg");
    const fillNowButton = document.getElementById("fillNowButton");
    const autoFillToggle = document.getElementById("autoFillToggle");
    const autoSubmitToggle = document.getElementById("autoSubmitToggle");

    function buildOtpauthUri() {
      if (storedOtpauthUri && /^otpauth:\/\/totp\//i.test(storedOtpauthUri)) return storedOtpauthUri;
      const issuer = "Leiden University";
      return "otpauth://totp/" + encodeURIComponent(issuer) +
             "?secret=" + encodeURIComponent(storedSecretKey) +
             "&issuer=" + encodeURIComponent(issuer);
    }

    function renderQrCode() {
      if (!qrCodeImg || typeof qrcode === "undefined" || !storedSecretKey) return;
      try {
        const qr = qrcode(0, "M"); // type 0 = auto-size, medium error correction
        qr.addData(buildOtpauthUri());
        qr.make();
        qrCodeImg.src = qr.createDataURL(4, 4);
      } catch (e) {
        console.error("AutoULCN: QR render error", e);
      }
    }

    if (autoFillToggle) {
      autoFillToggle.checked = result.Auto_Fill === true;
      autoFillToggle.addEventListener("change", function () {
        browserAPI.storage.local.set({ Auto_Fill: autoFillToggle.checked });
      });
    }

    // --- Auto-submit preference (default: off) ---
    if (autoSubmitToggle) {
      autoSubmitToggle.checked = result.Auto_Submit === true;
      autoSubmitToggle.addEventListener("change", function () {
        browserAPI.storage.local.set({ Auto_Submit: autoSubmitToggle.checked });
      });
    }

    // --- Live TOTP display ---
    let currentCode = null;
    async function renderTotp() {
      try {
        currentCode = await generateTOTP(storedSecretKey);
        if (totpCodeValueElement) totpCodeValueElement.textContent = currentCode;
        if (totpLabelElement) {
          const remaining = 30 - (Math.floor(Date.now() / 1000) % 30);
          totpLabelElement.textContent = `Current TOTP Code · ${remaining}s`;
        }
      } catch (e) {
        currentCode = null;
        if (totpCodeValueElement) totpCodeValueElement.textContent = "Invalid key";
      }
    }

    if (isULCN) {
      detectAndSaveSecretKey();
      if (storedSecretKey) {
        showElement(totpSection);
        if (secretKeyInputElement) hideElement(secretKeyInputElement.parentElement);
        hideElement(saveButton);
        if (statusElement) statusElement.textContent = "";

        renderTotp().then(() => {
          if (currentCode) {
            copyToClipboard(currentCode);
            showNotification('TOTP code copied to clipboard!');
          }
        });
        setInterval(renderTotp, 1000); // keep the displayed code fresh

        if (copyButton) copyButton.addEventListener("click", function () {
          if (currentCode) { copyToClipboard(currentCode); showNotification('Code copied!'); }
        });

        if (viewSecretButton) viewSecretButton.style.display = "block";
      } else {
        if (statusElement) statusElement.textContent = "Enter your TOTP secret key";
        if (secretKeyInputElement) showElement(secretKeyInputElement.parentElement);
        showElement(saveButton);
        hideElement(totpSection);
      }
    } else {
      if (statusElement) statusElement.textContent = "Open the Leiden login page and your code fills in automatically.";
      if (secretKeyInputElement) hideElement(secretKeyInputElement.parentElement);
      hideElement(saveButton);
      hideElement(totpSection);
      if (storedSecretKey && viewSecretButton) viewSecretButton.style.display = "block";
    }

    // --- Save secret manually ---
    if (saveButton) saveButton.addEventListener("click", function () {
      const secretKey = secretKeyInputElement.value.replace(/\s+/g, '').trim();
      if (secretKey && isLikelyBase32Key(secretKey)) {
        saveButton.textContent = "Saving...";
        saveButton.disabled = true;
        setTimeout(() => { saveSecretKey(); }, 300);
      } else {
        showNotification('Please enter a valid Base32 secret key', 'error');
        if (statusElement) statusElement.textContent = "That doesn't look like a valid key";
        secretKeyInputElement.focus();
      }
    });

    // --- Settings navigation (reachable from anywhere) ---
    function openSettings() {
      hideElement(mainPage);
      showElement(settingsPage);
      hideElement(settingsButton);
      hideElement(secretKeyDisplay);
      hideElement(qrCodeContainer);
      if (viewSecretButton) viewSecretButton.textContent = "View Secret Key";
    }
    if (settingsButton) settingsButton.addEventListener("click", openSettings);
    if (settingsLink) settingsLink.addEventListener("click", openSettings);

    if (backButton) backButton.addEventListener("click", function () {
      hideElement(settingsPage);
      showElement(mainPage);
      showElement(settingsButton);
      hideElement(secretKeyDisplay);
      hideElement(qrCodeContainer);
      if (viewSecretButton) viewSecretButton.textContent = "View Secret Key";
    });

    if (viewSecretButton) viewSecretButton.addEventListener("click", function () {
      if (!storedSecretKey || !secretKeyDisplay) return;
      if (secretKeyDisplay.classList.contains('hidden')) {
        secretKeyDisplay.textContent = storedSecretKey;
        renderQrCode();
        showElement(qrCodeContainer);
        showElement(secretKeyDisplay);
        viewSecretButton.textContent = "Hide Secret Key";
      } else {
        hideElement(secretKeyDisplay);
        hideElement(qrCodeContainer);
        viewSecretButton.textContent = "View Secret Key";
      }
    });

    if (resetButton) resetButton.addEventListener("click", function () {
      if (confirm('Are you sure you want to reset your secret key? You will need to enter it again.')) {
        resetButton.textContent = "Resetting...";
        resetButton.disabled = true;
        browserAPI.storage.local.remove('Secret_Key', function () {
          showNotification('Secret key reset successfully!');
          setTimeout(() => { location.reload(); }, 800);
        });
      }
    });

    // --- Manual "fill now" (fallback if auto-fill missed the field) ---
    if (fillNowButton) fillNowButton.addEventListener("click", function () {
      if (!currentTab) return;
      fillNowButton.textContent = "Sending…";
      sendMessageSafely(currentTab.id, { type: "AUTOULCN_FILL" }).then((delivered) => {
        fillNowButton.textContent = delivered ? "Sent!" : "Open login page first";
        setTimeout(() => { fillNowButton.textContent = "Fill Now"; }, 1500);
      });
    });
  });
});

// Auto-detect the secret on the enroll page when the popup is open there.
function detectAndSaveSecretKey() {
  const spanElement = document.querySelector('[data-hidden-value] > .display');
  if (!spanElement || !spanElement.innerText || spanElement.innerText === '••••••••••••••••') return;
  const secretKey = spanElement.innerText.replace(/\s+/g, '').trim();
  if (!isLikelyBase32Key(secretKey)) return;
  browserAPI.storage.local.set({ Secret_Key: secretKey }, function () {
    const statusElement = document.getElementById("status");
    if (statusElement) statusElement.textContent = "Secret Key Detected and Saved!";
    const inp = document.getElementById("secretKeyInput");
    const sb = document.getElementById("saveButton");
    if (inp) inp.style.display = "none";
    if (sb) sb.style.display = "none";
  });
}

function saveSecretKey() {
  const secretKey = document.getElementById("secretKeyInput").value.replace(/\s+/g, '').trim();
  if (secretKey && isLikelyBase32Key(secretKey)) {
    browserAPI.storage.local.set({ 'Secret_Key': secretKey }, function () {
      showNotification('Secret key saved successfully!');
      setTimeout(() => { location.reload(); }, 800);
    });
  }
}

function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => {
      console.log('Copied to clipboard using modern API');
    }).catch(() => {
      fallbackCopyToClipboard(text);
    });
  } else {
    fallbackCopyToClipboard(text);
  }
}

function fallbackCopyToClipboard(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}
