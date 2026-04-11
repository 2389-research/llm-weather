// ABOUTME: Netlify function to handle newsletter signups
// ABOUTME: Proxies to Buttondown API to avoid CSP issues with direct form submission

exports.handler = async function (event) {
  // Only allow POST
  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Method not allowed" }),
    };
  }

  // Parse the request body
  let email;
  try {
    const body = JSON.parse(event.body);
    email = body.email;
  } catch {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Invalid request body" }),
    };
  }

  // Validate email
  if (!email || !email.includes("@")) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Valid email required" }),
    };
  }

  // Get API key from environment
  const apiKey = process.env.BUTTONDOWN_API_KEY;
  if (!apiKey) {
    console.error("BUTTONDOWN_API_KEY not configured");
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Server configuration error" }),
    };
  }

  // Submit to Buttondown API
  try {
    const response = await fetch("https://api.buttondown.com/v1/subscribers", {
      method: "POST",
      headers: {
        Authorization: `Token ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email_address: email,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      return {
        statusCode: 200,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          success: true,
          message: "Check your email to confirm",
        }),
      };
    }

    // Handle already subscribed (409 or message contains "already subscribed")
    const errorDetail = data.detail || "";
    if (
      response.status === 409 ||
      errorDetail.toLowerCase().includes("already subscribed")
    ) {
      return {
        statusCode: 200,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          success: true,
          message: "You're already subscribed!",
        }),
      };
    }

    console.error("Buttondown API error:", data);
    return {
      statusCode: response.status,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: errorDetail || "Subscription failed" }),
    };
  } catch (err) {
    console.error("Network error:", err);
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        error: "Failed to connect to subscription service",
      }),
    };
  }
};
