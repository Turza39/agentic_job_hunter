# Browser Worker

Playwright-based browser automation service for filling and submitting job applications.

## Purpose

Handles all browser interactions:

- Opening application URLs
- Filling form fields
- Uploading files (CVs)
- Handling unknown fields
- Submitting forms
- Error handling and recovery

## Technology Stack

- **Language**: TypeScript
- **Browser Automation**: Playwright
- **Framework**: Express.js
- **Runtime**: Node.js

## Project Structure

```
browser-worker/
├── src/
│   ├── index.ts              # Express server
│   ├── types.ts              # TypeScript interfaces
│   ├── config.ts             # Configuration
│   ├── services/
│   │   ├── playwright.ts      # Playwright management
│   │   ├── form-filler.ts    # Form field detection & filling
│   │   └── error-handler.ts  # Error handling
│   ├── routes/
│   │   ├── application.ts    # Application endpoints
│   │   └── health.ts         # Health check
│   └── utils/
│       ├── logger.ts         # Logging
│       └── validators.ts     # Input validation
├── tests/
│   └── form-filler.test.ts
├── package.json
├── tsconfig.json
├── Dockerfile                # For containerization
└── README.md
```

## API Endpoints

### Health Check

```
GET /health
```

### Start Application

```
POST /application/start
Body: {
  "url": "https://careers.example.com/apply",
  "sessionId": "unique-session-id"
}
Response: {
  "status": "started",
  "sessionId": "unique-session-id"
}
```

### Fill Form Field

```
POST /application/fill
Body: {
  "sessionId": "unique-session-id",
  "fieldSelector": "input[name='name']",
  "value": "John Doe"
}
Response: {
  "success": true
}
```

### Get Unknown Fields

```
POST /application/get-unknown-fields
Body: {
  "sessionId": "unique-session-id"
}
Response: {
  "fields": [
    {
      "selector": "input[data-testid='current_salary']",
      "label": "Current Annual Salary",
      "placeholder": "e.g., 80000",
      "type": "number"
    }
  ]
}
```

### Submit Application

```
POST /application/submit
Body: {
  "sessionId": "unique-session-id"
}
Response: {
  "success": true,
  "message": "Application submitted successfully"
}
```

### Stop Session

```
POST /application/stop
Body: {
  "sessionId": "unique-session-id"
}
Response: {
  "success": true
}
```

## Key Features

### Form Detection

Intelligently detects:

- Text inputs
- Email fields
- Phone fields
- Dropdowns
- File upload fields
- Checkboxes and radio buttons
- Textareas

### File Upload

- Uploads CV files to specific fields
- Handles multiple file formats

### Error Recovery

- Takes screenshots on error
- Logs detailed error context
- Allows retry operations

### Session Management

- Multiple concurrent sessions
- Browser crash recovery
- Resource cleanup

## Implementation Phases

- **Phase 14**: Basic structure and setup
- **Phase 15**: Deterministic form filling
- **Phase 16**: Unknown field detection with LLM
- **Phase 21**: Advanced error handling and recovery

## Notes

- Run as a separate service
- Listens on port 3000 by default
- Each session runs in a separate browser context
- Screenshots saved for debugging
