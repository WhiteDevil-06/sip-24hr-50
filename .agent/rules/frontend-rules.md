# Subsystem Rules: Frontend Development (Ram Charan)

These rules apply to all web application development inside `frontend/`.

## 1. Framework & Language
- Use **Next.js (App Router)** with **TypeScript** and **Tailwind CSS**.
- Strict type checking (`"strict": true`) is required.
- Dynamic visualizations must use **Recharts**.

## 2. UI Aesthetics & Experience
- Implement a clean, modern, and accessible design system with harmonious color palettes.
- Include proper headings, descriptive labels, and accessible ARIA attributes.
- Ensure seamless responsive design across desktop, tablet, and mobile breakpoints.

## 3. Mandatory UI State Coverage
Every data-driven component or page must handle 4 explicit states:
1. **Loading State:** Skeletons or spinners during active data fetching.
2. **Empty State:** Clear, informative guidance when no forecast or historical data is loaded.
3. **Client Validation Error State:** Inline error messaging when inputs fail form validation.
4. **Backend Error State:** Non-crashing error banner/card when the backend service is offline or returns an error.

## 4. Truth in Data
- Mock data during early UI work must be prominently labeled `[MOCK DATA]`.
- Once connected to the backend, all charts and metrics must represent verified data from the API contract.
