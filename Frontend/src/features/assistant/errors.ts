/** Map assistant SSE / network errors to user-facing copy. */

export function formatAssistantError(
  message: string,
  code?: string | null,
): string {
  switch (code) {
    case "GROQ_TOOL_FAILED":
      return (
        message ||
        "I could not run an automated action. Try again or rephrase your question."
      );
    case "RATE_LIMIT":
      return "Too many AI requests. Please wait a moment and try again.";
    case "GROQ_ERROR":
      return message || "The AI service returned an error.";
    default:
      return message;
  }
}
