
export const getAIMessage = async (userQuery) => {

  try {
    // Not much point to use https for security here
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userQuery }),
    });

    const data = await response.json();
    return {
      role: "assistant",
      content: data.content,
    }
  } catch (error) {
    console.error("Error fetching AI message:", error);
    return {
      role: "assistant",
      content: "Sorry, I couldn't fetch the response. Please try again later.",
    }
  };
}

