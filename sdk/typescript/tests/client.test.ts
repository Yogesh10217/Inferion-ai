import { LLMEngineClient } from '../src/index.js';
import assert from 'node:assert';

const client = new LLMEngineClient({ baseUrl: 'http://localhost:8000', apiKey: 'test_key' });
assert.ok(client, 'Client should be instantiated');
console.log('TypeScript SDK tests passed.');
