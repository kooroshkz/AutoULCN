// Cross-browser compatibility
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

// Simple animation utilities
function showElement(element) {
  element.classList.remove('hidden');
  element.style.display = 'block';
}

function hideElement(element) {
  element.classList.add('hidden');
  element.style.display = 'none';
}

function showNotification(message, type = 'success') {
  console.log(`${type.toUpperCase()}: ${message}`);
  // Simple notification for debugging - you can enhance this later
}

browserAPI.tabs.query({ active: true, currentWindow: true }, function (tabs) {
  const currentTab = tabs[0];
  const isULCN = currentTab.url.startsWith("https://login.uaccess.leidenuniv.nl") || 
                 currentTab.url.startsWith("https://mfa.services.universiteitleiden.nl") ||
                 currentTab.url.startsWith("https://account.services.universiteitleiden.nl/portaal");

  browserAPI.storage.local.get('Secret_Key', function (result) {
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
    const viewSecretButton = document.getElementById("viewSecretButton");
    const resetButton = document.getElementById("resetButton");
    const backButton = document.getElementById("backButton");
    const secretKeyDisplay = document.getElementById("secretKeyDisplay");

    if (isULCN) {
      detectAndSaveSecretKey();
      if (storedSecretKey) {
        const totp = new jsOTP.totp();
        const totpCode = totp.getOtp(storedSecretKey);
        totpCodeValueElement.textContent = totpCode;
        
        showElement(totpSection);
        hideElement(secretKeyInputElement.parentElement);
        hideElement(saveButton);
        statusElement.textContent = "";
        
        copyToClipboard(totpCode);
        showNotification('TOTP code copied to clipboard!');

        copyButton.addEventListener("click", function () {
          copyToClipboard(totpCode);
          showNotification('Code copied!');
        });

        // Show view secret button in settings if secret key exists
        viewSecretButton.style.display = "block";
      } else {
        statusElement.textContent = "Enter your TOTP secret key";
        showElement(secretKeyInputElement.parentElement);
        showElement(saveButton);
        hideElement(totpSection);
      }
    } else {
      statusElement.textContent = "Navigate to ULCN login page to use this extension";
      hideElement(secretKeyInputElement.parentElement);
      hideElement(saveButton);
      hideElement(totpSection);
      
      // Show view secret button in settings if secret key exists even when not on ULCN page
      if (storedSecretKey) {
        viewSecretButton.style.display = "block";
      }
    }

    saveButton.addEventListener("click", function() {
      const secretKey = secretKeyInputElement.value.trim();
      if (secretKey) {
        saveButton.textContent = "Saving...";
        saveButton.disabled = true;
        
        setTimeout(() => {
          saveSecretKey();
        }, 500);
      } else {
        showNotification('Please enter a valid secret key', 'error');
        secretKeyInputElement.focus();
      }
    });

    settingsButton.addEventListener("click", function () {
      hideElement(mainPage);
      showElement(settingsPage);
      hideElement(settingsButton);
      hideElement(secretKeyDisplay);
      viewSecretButton.textContent = "View Secret Key";
    });

    backButton.addEventListener("click", function () {
      hideElement(settingsPage);
      showElement(mainPage);
      showElement(settingsButton);
      hideElement(secretKeyDisplay);
      viewSecretButton.textContent = "View Secret Key";
    });

    viewSecretButton.addEventListener("click", function () {
      if (storedSecretKey) {
        if (secretKeyDisplay.classList.contains('hidden')) {
          secretKeyDisplay.textContent = storedSecretKey;
          showElement(secretKeyDisplay);
          viewSecretButton.textContent = "Hide Secret Key";
        } else {
          hideElement(secretKeyDisplay);
          viewSecretButton.textContent = "View Secret Key";
        }
      }
    });

    resetButton.addEventListener("click", function () {
      if (confirm('Are you sure you want to reset your secret key? You will need to enter it again.')) {
        resetButton.textContent = "Resetting...";
        resetButton.disabled = true;
        
        browserAPI.storage.local.remove('Secret_Key', function () {
          showNotification('Secret key reset successfully!');
          setTimeout(() => {
            location.reload();
          }, 1000);
        });
      }
    });
  });
});

function detectAndSaveSecretKey() {
  const spanElement = document.querySelector('[data-hidden-value] > .display');
  if (spanElement && spanElement.innerText !== '••••••••••••••••') {
    const secretKey = spanElement.innerText;
    browserAPI.storage.local.set({ Secret_Key: secretKey }, function () {
      const statusElement = document.getElementById("status");
      statusElement.textContent = "Secret Key Detected and Saved!";
      document.getElementById("secretKeyInput").style.display = "none";
      document.getElementById("saveButton").style.display = "none";
    });
  }
}

function saveSecretKey() {
  const secretKey = document.getElementById("secretKeyInput").value.trim();
  if (secretKey) {
    browserAPI.storage.local.set({ 'Secret_Key': secretKey }, function () {
      showNotification('Secret key saved successfully!');
      setTimeout(() => {
        location.reload();
      }, 1000);
    });
  }
}

function copyToClipboard(text) {
  // Modern clipboard API with fallback
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
