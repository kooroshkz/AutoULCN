// popup.js
chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
  const currentTab = tabs[0];
  const isGoogle = currentTab.url.includes("google.com");
  const storedKey = localStorage.getItem("totpKey");

  const statusElement = document.getElementById("status");
  const userInputElement = document.getElementById("userInput");
  const saveButton = document.getElementById("saveButton");

  if (isGoogle) {
    if (storedKey) {
      const totp = new jsOTP.totp();
      const totpCode = totp.getOtp(storedKey);
      statusElement.textContent = "Current TOTP Code: " + totpCode;
      userInputElement.style.display = "none";
      saveButton.style.display = "none";
    } else {
      statusElement.textContent = "No TOTP Key stored. Enter one:";
      userInputElement.style.display = "block";
      saveButton.style.display = "block";
    }
  } else {
    statusElement.textContent = "You're not on Google";
    userInputElement.style.display = "none";
    saveButton.style.display = "none";
  }
});

function saveKey() {
  const totpKey = document.getElementById("userInput").value;
  localStorage.setItem("totpKey", totpKey);
  const totp = new jsOTP.totp();
  const totpCode = totp.getOtp(totpKey);
  document.getElementById("status").textContent = "Current TOTP Code: " + totpCode;
  document.getElementById("userInput").style.display = "none";
  document.getElementById("saveButton").style.display = "none";
}
