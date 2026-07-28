"""
Isolated Lua Scripts for Redis Rate Limiting.
Allows versioning, testing, and easy maintenance.
"""

# Sliding Window (using Sorted Sets)
# KEYS[1] - rate limit key
# ARGV[1] - current timestamp in ms
# ARGV[2] - window in ms
# ARGV[3] - limit
SLIDING_WINDOW_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

local clearBefore = now - window

-- Remove old elements
redis.call('ZREMRANGEBYSCORE', key, 0, clearBefore)

-- Count remaining
local count = redis.call('ZCARD', key)

if count < limit then
    redis.call('ZADD', key, now, now .. '-' .. string.sub(tostring(math.random()), 3, 8))
    redis.call('PEXPIRE', key, window)
    return {1, limit - count - 1}
else
    return {0, 0}
end
"""

# Token Bucket
# KEYS[1] - bucket key
# KEYS[2] - last timestamp key
# ARGV[1] - capacity
# ARGV[2] - refill_time_ms (time to refill full capacity)
# ARGV[3] - requested tokens (default 1)
# ARGV[4] - current timestamp in ms
TOKEN_BUCKET_LUA = """
local tokens_key = KEYS[1]
local timestamp_key = KEYS[2]
local capacity = tonumber(ARGV[1])
local refill_time_ms = tonumber(ARGV[2])
local requested = tonumber(ARGV[3])
local now = tonumber(ARGV[4])

local refill_rate = capacity / refill_time_ms

local last_tokens = tonumber(redis.call('GET', tokens_key))
if last_tokens == nil then
    last_tokens = capacity
end

local last_refreshed = tonumber(redis.call('GET', timestamp_key))
if last_refreshed == nil then
    last_refreshed = now
end

local delta = math.max(0, now - last_refreshed)
local filled_tokens = math.min(capacity, last_tokens + (delta * refill_rate))

local allowed = filled_tokens >= requested
local new_tokens = filled_tokens

if allowed then
    new_tokens = filled_tokens - requested
end

redis.call('SET', tokens_key, new_tokens)
redis.call('PEXPIRE', tokens_key, refill_time_ms * 2)

redis.call('SET', timestamp_key, now)
redis.call('PEXPIRE', timestamp_key, refill_time_ms * 2)

if allowed then
    return {1, math.floor(new_tokens)}
else
    return {0, math.floor(new_tokens)}
end
"""

# Fixed Window
# KEYS[1] - counter key
# ARGV[1] - limit
# ARGV[2] - window_seconds
FIXED_WINDOW_LUA = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])

local current = tonumber(redis.call('GET', key))
if current == nil then
    current = 0
end

if current < limit then
    local new_val = redis.call('INCR', key)
    if new_val == 1 then
        redis.call('EXPIRE', key, window)
    end
    return {1, limit - new_val}
else
    return {0, 0}
end
"""

# Leases for Concurrency
# KEYS[1] - scope count key (Hash: lease_id -> timestamp)
# ARGV[1] - limit
# ARGV[2] - ttl_seconds
# ARGV[3] - lease_id
# ARGV[4] - current timestamp in ms
ACQUIRE_LEASE_LUA = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])
local lease_id = ARGV[3]
local now = tonumber(ARGV[4])

-- Clean up expired leases
local leases = redis.call('HGETALL', key)
local active_count = 0
for i=1, #leases, 2 do
    local lid = leases[i]
    local expires_at = tonumber(leases[i+1])
    if expires_at < now then
        redis.call('HDEL', key, lid)
    else
        active_count = active_count + 1
    end
end

if active_count < limit then
    redis.call('HSET', key, lease_id, now + (ttl * 1000))
    redis.call('EXPIRE', key, ttl * 2)
    return {1, lease_id}
else
    return {0, ""}
end
"""
