# Deployment Information

## Public URL
https://2a202600030daoquangthang-production.up.railway.app (Placeholder)

## Platform
Railway


## Test Commands

### Health Check
```bash
curl https://2a202600030daoquangthang-production.up.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://2a202600030daoquangthang-production.up.railway.app/ask \
  -H "X-API-Key: thang-ai-agent-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello Agent!"}'
```

## Environment Variables Set
- PORT=8000
- AGENT_API_KEY=thang-ai-agent-2026
- ENVIRONMENT=production
- APP_NAME="AI Agent Production"

## Screenshots
Screenshots of the deployment and test results can be found in the `screenshots/` directory (if provided).
