const BASE_URL = process.env.REACT_APP_USE_DOCKER === "true"
  ? process.env.REACT_APP_BACKEND_HOST
  : "http://localhost:8000";

export const getAIMessage = async (userQuery) => {

  try {    
    console.log("Using backend URL:", BASE_URL);
    const response = await fetch(`${BASE_URL}/chat`, {
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

