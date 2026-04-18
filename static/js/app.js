document.addEventListener("DOMContentLoaded", () => {
    const composer = document.querySelector(".composer");
    const textarea = document.querySelector("#message");
    const chatLog = document.querySelector(".chat-log");

    // Scroll the chat container itself, not the whole page.
    if (chatLog) {
      chatLog.scrollTop = chatLog.scrollHeight;
    }

    if (textarea) {
      // Keep the input ready for the next message.
      textarea.focus();

      textarea.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
          event.preventDefault();
          composer?.requestSubmit();
        }
      });
    }
  });
