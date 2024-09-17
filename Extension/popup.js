chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
  const currentTab = tabs[0];
  const isULCN = currentTab.url.startsWith("https://login.uaccess.leidenuniv.nl") || currentTab.url.startsWith("https://mfa.services.universiteitleiden.nl");

  const storedSecretKey = localStorage.getItem("Secret_Key");
  const statusElement = document.getElementById("status");
  const secretKeyInputElement = document.getElementById("secretKeyInput");
  const saveButton = document.getElementById("saveButton");

  if (isULCN) {
    if (storedSecretKey) {
      const totp = new jsOTP.totp();
      const totpCode = totp.getOtp(storedSecretKey);
      copyToClipboard(totpCode);
      statusElement.textContent = "Current TOTP Code: " + totpCode;
      secretKeyInputElement.style.display = "none";
      saveButton.style.display = "none";
    } else {
      statusElement.textContent = "Enter your TOTP secret key:";
      secretKeyInputElement.style.display = "block";
      saveButton.style.display = "block";
    }
  } else {
    statusElement.textContent = "You're not on ULCN login page";
    secretKeyInputElement.style.display = "none";
    saveButton.style.display = "none";
  }

  document.getElementById("saveButton").addEventListener("click", saveSecretKey);
});

function saveSecretKey() {
  const secretKey = document.getElementById("secretKeyInput").value;
  localStorage.setItem("Secret_Key", secretKey);

  const totp = new jsOTP.totp();
  const totpCode = totp.getOtp(secretKey);
  copyToClipboard(totpCode);
  document.getElementById("status").textContent = "Current TOTP Code: " + totpCode;
  document.getElementById("secretKeyInput").style.display = "none";
  document.getElementById("saveButton").style.display = "none";
}

function copyToClipboard(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}
