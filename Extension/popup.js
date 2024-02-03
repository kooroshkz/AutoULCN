chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
  const currentTab = tabs[0];
  const isULCN = currentTab.url.startsWith("https://login.uaccess.leidenuniv.nl") || currentTab.url.startsWith("https://mfa.services.universiteitleiden.nl");

  const storedUsername = localStorage.getItem("Username");
  const storedPassword = localStorage.getItem("Password");
  const storedSecretKey = localStorage.getItem("Secret_Key");

  const statusElement = document.getElementById("status");
  const userInputElement = document.getElementById("userInput");
  const passwordInputElement = document.getElementById("passwordInput");
  const secretKeyInputElement = document.getElementById("secretKeyInput");
  const saveButton = document.getElementById("saveButton");

  if (isULCN) {
    if (storedUsername && storedPassword && storedSecretKey) {
      const totp = new jsOTP.totp();
      const totpCode = totp.getOtp(storedSecretKey);
      copyToClipboard(totpCode);
      statusElement.textContent = "Current TOTP Code: " + totpCode;
      userInputElement.style.display = "none";
      passwordInputElement.style.display = "none";
      secretKeyInputElement.style.display = "none";
      saveButton.style.display = "none";
    } else {
      statusElement.textContent = "Enter your ULCN credentials and TOTP secret key:";
      userInputElement.style.display = "block";
      passwordInputElement.style.display = "block";
      secretKeyInputElement.style.display = "block";
      saveButton.style.display = "block";
    }
  } else {
    statusElement.textContent = "You're not on ULCN login page";
    userInputElement.style.display = "none";
    passwordInputElement.style.display = "none";
    secretKeyInputElement.style.display = "none";
    saveButton.style.display = "none";
  }

  document.getElementById("saveButton").addEventListener("click", saveCredentials);
});


function saveCredentials() {
  const username = document.getElementById("userInput").value;
  const password = document.getElementById("passwordInput").value;
  const secretKey = document.getElementById("secretKeyInput").value;

  localStorage.setItem("Username", username);
  localStorage.setItem("Password", password);
  localStorage.setItem("Secret_Key", secretKey);

  const totp = new jsOTP.totp();
  const totpCode = totp.getOtp(secretKey);
  copyToClipboard(totpCode);
  document.getElementById("status").textContent = "Current TOTP Code: " + totpCode;
  document.getElementById("userInput").style.display = "none";
  document.getElementById("passwordInput").style.display = "none";
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
