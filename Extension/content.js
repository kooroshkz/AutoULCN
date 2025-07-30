// Cross-browser compatibility
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

const detectAndSaveSecretKey = () => {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.target.classList.contains('display') && mutation.target.innerText !== '••••••••••••••••') {
                const secretKey = mutation.target.innerText;
                browserAPI.storage.local.set({ Secret_Key: secretKey }, () => {
                    showSecretKeyNotification(secretKey);
                });
                observer.disconnect();
            }
        });
    });

    const spanElement = document.querySelector('[data-hidden-value] > .display');
    if (spanElement) {
        observer.observe(spanElement, { childList: true });
    }
};

const showSecretKeyNotification = (secretKey) => {
    const notificationDiv = document.createElement('div');
    notificationDiv.style.position = 'fixed';
    notificationDiv.style.bottom = '20px';
    notificationDiv.style.right = '20px';
    notificationDiv.style.padding = '10px';
    notificationDiv.style.backgroundColor = '#28a745';
    notificationDiv.style.color = '#fff';
    notificationDiv.style.zIndex = '9999';
    notificationDiv.style.borderRadius = '5px';
    notificationDiv.style.fontFamily = 'Arial, sans-serif';

    const message = document.createElement('p');
    message.innerText = `Secret Key Detected and Saved: ${secretKey}`;
    notificationDiv.appendChild(message);

    document.body.appendChild(notificationDiv);

    setTimeout(() => {
        notificationDiv.remove();
    }, 5000);
};

if (document.readyState === 'complete' || document.readyState === 'interactive') {
    detectAndSaveSecretKey();
} else {
    document.addEventListener('DOMContentLoaded', detectAndSaveSecretKey);
}
