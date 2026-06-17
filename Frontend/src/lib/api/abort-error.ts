/** True when a fetch/stream was cancelled via AbortController (not a real failure). */
export function isAbortError(err: unknown): boolean {
  if (err == null) return false;
  if (typeof DOMException !== "undefined" && err instanceof DOMException) {
    return err.name === "AbortError";
  }
  if (err instanceof Error) {
    if (err.name === "AbortError") return true;
    const msg = err.message.toLowerCase();
    return (
      msg.includes("aborted") ||
      msg.includes("abort") ||
      msg === "the user aborted a request"
    );
  }
  return false;
}
