import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom Metrics
export const errorRate = new Rate('errors');
export const ttftMs = new Trend('time_to_first_token_ms');
export const tokensGenerated = new Counter('total_tokens_generated');

// Benchmark Configuration targeting 10,000+ RPS sustained throughput
export const options = {
  scenarios: {
    sustained_10k_rps: {
      executor: 'ramping-arrival-rate',
      startRate: 1000,
      timeUnit: '1s',
      preAllocatedVUs: 1000,
      maxVUs: 12000,
      stages: [
        { duration: '10s', target: 2000 },   // Warm-up to 2k RPS
        { duration: '20s', target: 5000 },   // Scale to 5k RPS
        { duration: '30s', target: 10000 },  // Sustained Peak 10k RPS
        { duration: '30s', target: 10000 },  // Maintain 10k RPS
        { duration: '10s', target: 0 },      // Ramp-down
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<25', 'p(99)<50'], // P95 < 25ms, P99 < 50ms
    http_req_failed: ['rate<0.001'],             // Error rate < 0.1%
    errors: ['rate<0.001'],
  },
};

const BASE_URL = __ENV.TARGET_URL || 'http://localhost:8005';

const TENANTS = ['org-acme-corp', 'org-techstart', 'org-apex-global'];
const WORKSPACES = ['ws-engineering', 'ws-finance', 'ws-data-science'];

function getRandomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export default function () {
  const tenant = getRandomItem(TENANTS);
  const workspace = getRandomItem(WORKSPACES);

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer sk_live_${workspace}_${Math.floor(Math.random() * 9000 + 1000)}`,
    'X-Organization-Id': tenant,
    'X-Workspace-Id': workspace,
  };

  const rand = Math.random();

  if (rand < 0.5) {
    // 50% Non-Streaming Chat Completions
    const payload = JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'K6 high-concurrency 10k RPS benchmark.' }],
      metadata: { mock: true },
    });

    const res = http.post(`${BASE_URL}/v1/chat/completions`, payload, { headers });
    const success = check(res, {
      'status is 200': (r) => r.status === 200,
      'has choices payload': (r) => r.json('choices') !== undefined,
    });
    errorRate.add(!success);
    if (success) {
      tokensGenerated.add(42);
    }
  } else if (rand < 0.75) {
    // 25% Streaming Chat Completions
    const payload = JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'K6 SSE streaming latency check.' }],
      stream: true,
      metadata: { mock: true },
    });

    const startTime = Date.now();
    const res = http.post(`${BASE_URL}/v1/chat/completions`, payload, { headers });
    const elapsed = Date.now() - startTime;

    const success = check(res, {
      'status is 200': (r) => r.status === 200,
    });
    errorRate.add(!success);
    if (success) {
      ttftMs.add(elapsed);
      tokensGenerated.add(25);
    }
  } else if (rand < 0.90) {
    // 15% Embeddings Generation
    const payload = JSON.stringify({
      model: 'text-embedding-3-small',
      input: 'K6 vector embedding generation high throughput benchmark.',
    });

    const res = http.post(`${BASE_URL}/v1/embeddings`, payload, { headers });
    const success = check(res, {
      'status is 200': (r) => r.status === 200,
      'has embedding data': (r) => r.json('data') !== undefined,
    });
    errorRate.add(!success);
  } else {
    // 10% RAG Knowledge Search
    const payload = JSON.stringify({
      query: 'K6 load testing vector search 10k RPS benchmark',
      top_k: 5,
    });

    const res = http.post(`${BASE_URL}/v1/knowledge/search`, payload, { headers });
    const success = check(res, {
      'status is 200': (r) => r.status === 200,
      'has results': (r) => r.json('results') !== undefined,
    });
    errorRate.add(!success);
  }
}
