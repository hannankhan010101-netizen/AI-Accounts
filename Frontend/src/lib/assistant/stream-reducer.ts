/** Pure helpers for SSE stream state (testable without vitest). */

export function appendStreamToken(current: string, token: string): string {
  return current + token;
}

export function flushStreamToMessages(
  messages: { role: string; content: string }[],
  streamingContent: string,
): { role: string; content: string }[] {
  const trimmed = streamingContent.trim();
  if (!trimmed) return messages;
  return [...messages, { role: "assistant", content: trimmed }];
}
