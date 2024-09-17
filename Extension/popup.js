chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
  const currentTab = tabs[0];
  const isULCN = currentTab.url.startsWith("https://login.uaccess.leidenuniv.nl") || currentTab.url.startsWith("https://mfa.services.universiteitleiden.nl");

  const storedSecretKey = localStorage.getItem("Secret_Key");
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
    if (storedSecretKey) {
      const totp = new jsOTP.totp();
      const totpCode = totp.getOtp(storedSecretKey);
      totpCodeValueElement.textContent = totpCode;
      totpSection.style.display = "flex";
      secretKeyInputElement.style.display = "none";
      saveButton.style.display = "none";
      copyToClipboard(totpCode);  // Automatically copy TOTP on load

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
    localStorage.removeItem("Secret_Key");
    location.reload();  // Refresh the popup to go back to the initial state
  });
});

function saveSecretKey() {
  const secretKey = document.getElementById("secretKeyInput").value;
  localStorage.setItem("Secret_Key", secretKey);
  location.reload();  // Refresh to show TOTP code
}

function copyToClipboard(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}
