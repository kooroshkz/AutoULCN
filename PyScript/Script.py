import pyotp

# Replace 'your_secret_key' with your actual secret key
secret_key = 'Secret_Key'
totp = pyotp.TOTP(secret_key)

# Generate a TOTP code
totp_code = totp.now()
print("TOTP Code:", totp_code)
