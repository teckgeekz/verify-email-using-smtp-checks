# Flask API Integration Setup

This document explains how to set up the Flask API integration with the Next.js frontend.

## Environment Variables

Create a `.env.local` file in the `apps/nextjs` directory with the following variables:

```env
# Flask API Configuration
NEXT_PUBLIC_FLASK_URL=http://127.0.0.1:5000

# App Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Stripe Configuration (if using payments)
STRIPE_API_KEY=your_stripe_api_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# PostHog Configuration (optional)
NEXT_PUBLIC_POSTHOG_KEY=your_posthog_key_here
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

## Flask API Setup

1. Make sure your Flask API is running on the specified URL (default: http://127.0.0.1:5000)
2. The Flask API should have the following endpoints:
   - `POST /` - Email Finder (no authentication required)
   - `POST /single-verify` - Single Email Verification (no authentication required)
   - `GET /bulk-verify` - Get bulk verification usage (requires Firebase authentication)
   - `POST /bulk-verify` - Bulk Email Verification (requires Firebase authentication)
   - `GET /download/<filename>` - Download verification results (no authentication required)

## Authentication Requirements

- **Email Finder** and **Single Email Verify**: No authentication required
- **Bulk Email Verify**: Requires Firebase authentication (usage limits handled by frontend)
- The Flask API uses Firebase ID tokens for authentication via Authorization headers

## New Pages Added

### 1. Email Finder (`/email-finder`)
- Connects to Flask API route `/`
- Allows users to find emails by providing name, company, and domain
- Shows LinkedIn profile and verified email addresses

### 2. Single Email Verify (`/single-verify`)
- Connects to Flask API route `/single-verify`
- Allows users to verify a single email address
- Shows validation status

### 3. Bulk Email Verify (`/bulk-verify`)
- Connects to Flask API route `/bulk-verify`
- Allows users to upload CSV/Excel files with email addresses
- Processes all emails in the file (no usage limits)
- Provides download functionality for results

## Navigation

The navigation has been updated to include the new email tools:
- Email Finder
- Single Verify
- Bulk Verify

## API Service

The Flask API integration is handled by `src/lib/flask-api.ts` which provides:
- Type-safe interfaces for all API calls
- Error handling
- File upload support
- Download functionality

## Usage

1. Start your Flask API server
2. Set the `NEXT_PUBLIC_FLASK_URL` environment variable
3. Start the Next.js development server
4. Navigate to the new email tool pages

## File Structure

```
src/
├── app/[lang]/(marketing)/
│   ├── email-finder/
│   │   └── page.tsx
│   ├── single-verify/
│   │   └── page.tsx
│   └── bulk-verify/
│       └── page.tsx
├── lib/
│   └── flask-api.ts
└── config/
    ├── ui/marketing.ts (updated)
    └── dictionaries/en.json (updated)
``` 