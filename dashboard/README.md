# Dashboard

Web-based dashboard for configuration, monitoring, and manual management.

## Purpose

Provides UI for:

- Viewing collected and matched jobs
- Approving/rejecting applications
- Managing preferences
- Uploading CVs
- Configuring companies and job sources
- Tracking application status
- Viewing notifications

## Features (by phase)

### Core Dashboard

- Job statistics (found, matched, applied)
- Application status overview
- Recent notifications

### Preferences Management

- Location preferences
- Experience level filters
- Salary expectations
- Remote/hybrid/onsite toggle
- Keywords to include/exclude
- Minimum match score threshold

### Companies & Sources

- List configured companies
- Enable/disable job sources
- View career page URLs
- Polling status

### CV Management

- Upload new CVs
- View CV categories and skills
- Mark active/inactive
- Download CVs

### Job Listings

- View all collected jobs
- See match scores
- Filter by status
- View job details

### Applications

- View application status
- See filled forms
- Check submission status
- Track interviews and outcomes

## Technology Stack Options

The dashboard can be built with any modern framework:

- **React** / Next.js (if you prefer modern SPA)
- **Vue** / Nuxt (if you prefer Vue)
- **Svelte** / SvelteKit
- **Server-rendered** (HTML/CSS/JS templates with FastAPI)

Start simple! A server-rendered HTML dashboard is perfectly fine for V1.

## Project Structure

```
dashboard/
├── src/
│   ├── pages/
│   ├── components/
│   ├── services/
│   │   └── api.ts        # API client
│   ├── styles/
│   └── main.ts
├── public/
├── package.json
├── tsconfig.json
└── README.md
```

## Key Pages

1. **Dashboard** - Overview and stats
2. **Jobs** - Browse collected jobs
3. **Applications** - View all applications
4. **Preferences** - Configure job filters
5. **CVs** - Upload and manage CVs
6. **Companies** - Configure job sources
7. **Notifications** - View notification history
8. **Settings** - API keys, Telegram config, etc.

## Implementation Phase

- **Phase 20**: After core automation is working

## Important Principles

- **Read-only initially** - No direct modifications until trusted
- **Approval workflow** - Critical actions require confirmation
- **Transparent logging** - All actions are logged
- **Real-time updates** - Use WebSocket or polling for live status

## Notes

- Start with a simple HTML/CSS dashboard
- Add more sophistication gradually
- Focus on usability over aesthetics for V1
