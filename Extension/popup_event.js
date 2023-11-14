document.getElementById('saveButton').addEventListener('click', saveCredentials);

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
