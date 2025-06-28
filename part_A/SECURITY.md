# Security Configuration

## Overview
This application uses environment variables for all sensitive credentials. **No API keys, tokens, or secrets are hardcoded in the source code.**

## Environment Variables
The application expects the following environment variables to be set in a `config.env` file:

```
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=your_twilio_phone_number_here
EMERGENCY_NUMBERS=+1234567890,+0987654321
```

## Setup Instructions
1. Copy `config.env.example` to `config.env`
2. Fill in your actual Twilio credentials in `config.env`
3. The `config.env` file is automatically ignored by git (see `.gitignore`)

## Security Features
- All credentials loaded from environment variables only
- No hardcoded secrets in source code
- `config.env` file is gitignored to prevent accidental commits
- Graceful degradation when credentials are missing
- Clear error messages when configuration is incomplete

## Twilio Configuration
To enable SMS alerts:
1. Sign up for a Twilio account
2. Get your Account SID and Auth Token from the Twilio Console
3. Get a Twilio phone number for sending SMS
4. Add these credentials to your `config.env` file

## Emergency Numbers
Add phone numbers (with country codes) to the `EMERGENCY_NUMBERS` variable, separated by commas.

Example: `EMERGENCY_NUMBERS=+1234567890,+0987654321` 