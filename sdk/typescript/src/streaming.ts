export interface ChatCompletionChunk {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    delta: { content?: string };
    finish_reason: string | null;
  }>;
}

export async function* streamIterator(response: Response): AsyncGenerator<ChatCompletionChunk, void, unknown> {
  if (!response.body) {
    throw new Error("Response body is null or undefined.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith(":")) continue;

        if (trimmed.startsWith("data: ")) {
          const dataStr = trimmed.slice(6).trim();
          if (dataStr === "[DONE]") return;

          try {
            const chunk: ChatCompletionChunk = JSON.parse(dataStr);
            yield chunk;
          } catch (err) {
            // Ignore parse errors on transient chunks
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
