# Load Testing for WaveSpeed Workshop

This directory contains load testing scripts to simulate high-volume traffic to our application.

## Prerequisites

- [k6](https://k6.io/docs/getting-started/installation/) - A modern load testing tool

## Available Tests

- `k6/http-test.js` - HTTP load test simulating gradual traffic increase

## Running the Tests

### Basic HTTP Load Test

To run the basic HTTP load test:

```bash
# First make sure your application is running and accessible at http://localhost:8080

# Then run the test
k6 run load-testing/k6/http-test.js
```

### Custom Load Profiles

You can modify the load profile by passing options:

```bash
# Run with 50 virtual users for 30 seconds
k6 run --vus 50 --duration 30s load-testing/k6/http-test.js

# Run with a custom environment variable
k6 run -e TARGET_URL=http://your-custom-url load-testing/k6/http-test.js
```

## Interpreting Results

The k6 load test will output:

- HTTP request metrics (response times, request rates, etc.)
- Custom metrics (success rates, request counters)
- Threshold validation (pass/fail based on performance goals)

Key metrics to watch:
- `http_req_duration` - How long requests take
- `http_reqs` - Request throughput
- `http_req_failed` - Failed request rate
- `success_rate` - Custom check success rate

## Performance Goals

The default thresholds in the test scripts expect:
- 95% of requests to complete in under 500ms
- Less than 10% of requests to fail
- More than 90% of custom checks to pass 