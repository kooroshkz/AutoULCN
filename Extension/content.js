// content.js
const fillForm = () => {
    const userIdInput = document.querySelector('input[name="Ecom_User_ID"]');
    const passwordInput = document.querySelector('input[name="Ecom_Password"]');
    const loginButton = document.querySelector('button[name="login"]');
    
    if (userIdInput && passwordInput) { // TODO: localStorage.getItem("Username") and localStorage.getItem("Password") are null
        userIdInput.value = localStorage.getItem("Username");
        passwordInput.value = localStorage.getItem("Password");
        loginButton.click();
    }
};

// Execute the function when the DOM is ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    fillForm();
} else {
    document.addEventListener('DOMContentLoaded', fillForm);
}
