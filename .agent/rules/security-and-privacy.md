# Subsystem Rules: Security & Privacy

These rules prevent credential leaks and ensure secure data handling and application architecture.

## 1. Secret Protection
- Real credentials, API keys, tokens, or private endpoints must never be checked into version control.
- All secrets must be stored in `.env` or `.env.local` files, which must remain in `.gitignore`.
- Provide `.env.example` with dummy values for documentation and onboarding.

## 2. Browser Environment Variable Safety
- In Next.js, only variables meant to be public may be prefixed with `NEXT_PUBLIC_`.
- Private server configurations (API secrets, private hostnames, tokens) must never use the `NEXT_PUBLIC_` prefix.

## 3. Input Validation & API Hardening
- Backend endpoints must validate payload structure, lengths, data types, and value bounds using Pydantic schemas.
- Reject NaN, Inf, and malformed inputs with 400 Bad Request.
- Set appropriate CORS origin restrictions rather than open wildcards in production configurations.
