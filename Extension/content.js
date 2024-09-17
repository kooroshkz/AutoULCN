const fillForm = () => {
    const totp = new jsOTP.totp();
    const storedSecretKey = localStorage.getItem("Secret_Key");

    if (storedSecretKey) {
        const totpCode = totp.getOtp(storedSecretKey);
        copyToClipboard(totpCode);
    }
};

// Execute the function when the DOM is ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    fillForm();
} else {
    document.addEventListener('DOMContentLoaded', fillForm);
}

function copyToClipboard(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}
