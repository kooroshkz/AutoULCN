chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
  const currentTab = tabs[0];
  const isULCN = currentTab.url.startsWith("https://login.uaccess.leidenuniv.nl") || 
                 currentTab.url.startsWith("https://mfa.services.universiteitleiden.nl") ||
                 currentTab.url.startsWith("https://account.services.universiteitleiden.nl/portaal");

  chrome.storage.local.get('Secret_Key', function (result) {
    const storedSecretKey = result.Secret_Key;
    const statusElement = document.getElementById("status");
    const secretKeyInputElement = document.getElementById("secretKeyInput");
    const saveButton = document.getElementById("saveButton");
    const totpCodeValueElement = document.getElementById("totpCodeValue");
    const copyButton = document.getElementById("copyButton");
    const totpSection = document.getElementById("totpSection");
    const settingsButton = document.getElementById("settingsButton");
    const mainPage = document.getElementById("mainPage");
    const settingsPage = document.getElementById("settingsPage");
    const resetButton = document.getElementById("resetButton");
    const backButton = document.getElementById("backButton");

    if (isULCN) {
      detectAndSaveSecretKey();
      if (storedSecretKey) {
        const totp = new jsOTP.totp();
        const totpCode = totp.getOtp(storedSecretKey);
        totpCodeValueElement.textContent = totpCode;
        totpSection.style.display = "flex";
        secretKeyInputElement.style.display = "none";
        saveButton.style.display = "none";
        copyToClipboard(totpCode);

        copyButton.addEventListener("click", function () {
          copyToClipboard(totpCode);
        });
      } else {
        statusElement.textContent = "Enter your TOTP secret key:";
        secretKeyInputElement.style.display = "block";
        saveButton.style.display = "block";
        totpSection.style.display = "none";
      }
    } else {
      statusElement.textContent = "You're not on ULCN login page";
      secretKeyInputElement.style.display = "none";
      saveButton.style.display = "none";
      totpSection.style.display = "none";
    }

    saveButton.addEventListener("click", saveSecretKey);

    settingsButton.addEventListener("click", function () {
      mainPage.style.display = "none";
      settingsPage.style.display = "block";
      settingsButton.style.display = "none";
    });

    backButton.addEventListener("click", function () {
      settingsPage.style.display = "none";
      mainPage.style.display = "block";
      settingsButton.style.display = "inline";
    });

    resetButton.addEventListener("click", function () {
      chrome.storage.local.remove('Secret_Key', function () {
        location.reload();
      });
    });
  });
});

function detectAndSaveSecretKey() {
  const spanElement = document.querySelector('[data-hidden-value] > .display');
  if (spanElement && spanElement.innerText !== '••••••••••••••••') {
    const secretKey = spanElement.innerText;
    chrome.storage.local.set({ Secret_Key: secretKey }, function () {
      const statusElement = document.getElementById("status");
      statusElement.textContent = "Secret Key Detected and Saved!";
      document.getElementById("secretKeyInput").style.display = "none";
      document.getElementById("saveButton").style.display = "none";
    });
  }
}

function saveSecretKey() {
  const secretKey = document.getElementById("secretKeyInput").value;
  chrome.storage.local.set({ 'Secret_Key': secretKey }, function () {
    location.reload();
  });
}

function copyToClipboard(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}
