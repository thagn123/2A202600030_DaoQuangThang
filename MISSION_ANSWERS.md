# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **Hardcoded Secrets**: API keys like `sk-...` were written directly in `app.py`.
2. **Fixed Port/Host**: Using `port=8000` and `host="localhost"` prevents portability in cloud environments.
3. **Debug Mode Enabled**: `debug=True` in production can leak system internals and slow down the app.
4. **Missing Health Checks**: No `/health` endpoint for the container orchestrator to monitor application status.
5. **Print Statements for Logging**: Using `print()` instead of structured logging makes it impossible to aggregate logs effectively.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcoded | Environment Variables | Security and portability across environments. |
| Health  | None | /health & /ready | Orchestrators (K8s/Docker) need to know status. |
| Logging | print() | Structured JSON | Efficient debugging and log aggregation. |
| Shutdown| Sudden | Graceful (SIGTERM) | Completion of in-flight requests before exit. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image**: `python:3.11-slim` (or `python:3.11` in basic).
2. **Working directory**: `/app`.
3. **COPY requirements first**: To utilize Docker's layer caching; if requirements don't change, `pip install` is skipped.
4. **CMD vs ENTRYPOINT**: `CMD` sets a default command that can be overridden; `ENTRYPOINT` is the fixed executable that `CMD` arguments are passed to.

### Exercise 2.3: Image size comparison
- **Develop (Basic)**: ~1 GB
- **Production (Multi-stage)**: ~150-200 MB
- **Difference**: ~80% reduction in size.

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- **Auth**: Correctly returns 401 Unauthorized when `X-API-Key` is missing.
- **Rate Limit**: Returns 429 Too Many Requests after 20 req/min (configured value).
- **Cost Guard**: Returns 503 or 402 once the daily budget of $5.0 (demo value) is reached.

### Exercise 4.4: Cost guard implementation
Implemented total tokens estimation based on string length (mock calculation) and tracked against a running total in-memory (extensible to Redis for stateless scaling).

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Stateless Design**: All configuration and potentially session state (Redis) are externalized, allowing horizontal scaling to 3+ instances using Docker Compose.
- **Graceful Shutdown**: SIGTERM is handled to log the shutdown event and allow any pending requests 30 seconds to finish.
