/**
 * API client for communicating with the FastAPI backend
 */

// Use relative path when deployed on Vercel (same domain)
// Use localhost:8000 for local development
const getApiBaseUrl = () => {
  // If explicitly set via environment variable, use that
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // For local development, always use localhost:8000
  // (both client-side and server-side)
  if (typeof window !== 'undefined') {
    // In browser - check if we're on localhost (local dev)
    // If so, use localhost:8000, otherwise use relative path (for Vercel)
    const isLocalhost = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1';
    return isLocalhost ? 'http://localhost:8000' : '';
  }
  
  // Server-side rendering - use localhost:8000 for local dev
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

export interface ChatResponse {
  reply: string;
}

export interface ChatError {
  detail: string;
}

/**
 * Parses error messages to provide user-friendly feedback
 * @param errorDetail - The error detail string from the API
 * @returns A user-friendly error message
 */
function parseErrorMessage(errorDetail: string): string {
  // Check for OpenAI quota/billing errors
  if (errorDetail.includes('insufficient_quota') || errorDetail.includes('quota')) {
    return 'OpenAI API quota exceeded. Please check your OpenAI account billing and usage limits. You may need to add payment information or upgrade your plan.';
  }
  
  // Check for API key errors
  if (errorDetail.includes('OPENAI_API_KEY') || errorDetail.includes('api key')) {
    return 'OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable in your backend.';
  }
  
  // Check for authentication errors
  if (errorDetail.includes('401') || errorDetail.includes('unauthorized') || errorDetail.includes('Invalid API key')) {
    return 'Invalid OpenAI API key. Please check your API key configuration.';
  }
  
  // Check for rate limiting
  if (errorDetail.includes('429') || errorDetail.includes('rate limit')) {
    return 'Rate limit exceeded. Please wait a moment and try again.';
  }
  
  // Return the original error if no specific pattern matches
  return errorDetail;
}

/**
 * Sends a message to the chat API and returns the assistant's reply
 * @param message - The user's message to send
 * @returns Promise resolving to the chat response
 * @throws Error if the API request fails
 */
export async function sendMessage(message: string): Promise<ChatResponse> {
  const url = `${API_BASE_URL}/api/chat`;
  console.log('📤 Frontend: Sending request to:', url);
  console.log('📤 Frontend: Message:', message);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    
    console.log('📥 Frontend: Received response status:', response.status);

    if (!response.ok) {
      const errorData: ChatError = await response.json().catch(() => ({
        detail: `HTTP error! status: ${response.status}`,
      }));
      const userFriendlyMessage = parseErrorMessage(errorData.detail || `Request failed with status ${response.status}`);
      throw new Error(userFriendlyMessage);
    }

    const data: ChatResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error) {
      // Network errors or other fetch errors
      if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
        throw new Error(
          'Unable to connect to the server. Please make sure the backend is running on http://localhost:8000'
        );
      }
      throw error;
    }
    throw new Error('An unexpected error occurred');
  }
}

