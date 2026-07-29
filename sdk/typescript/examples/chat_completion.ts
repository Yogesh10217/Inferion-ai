import { LLMEngineClient } from '../src/index.js';

const client = new LLMEngineClient({ baseUrl: 'http://localhost:8000', apiKey: 'test_key' });
console.log('TypeScript SDK initialized');
