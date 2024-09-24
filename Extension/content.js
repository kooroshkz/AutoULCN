const fillTOTPForm = () => {
    const totp = new jsOTP.totp();

    chrome.storage.local.get('Secret_Key', function(result) {
        const storedSecretKey = result.Secret_Key;

        if (storedSecretKey) {
            const totpCode = totp.getOtp(storedSecretKey);

            // Locate the TOTP input field using its ID 'nffc'
            const totpInputField = document.getElementById('nffc');
            if (totpInputField) {
                totpInputField.value = totpCode; // Auto-fill TOTP code into the field

                // Optionally auto-submit the form if required
                const nextButton = document.getElementById('loginButton2');
                if (nextButton) {
                    nextButton.click(); // Simulate clicking the "Next" button to submit the form
                }
            }
        }
    });
};

// Trigger function when the page is loaded
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    fillTOTPForm();
} else {
    document.addEventListener('DOMContentLoaded', fillTOTPForm);
}
