import React from 'react';

// Helper function to ensure URL has no trailing slash
const normalizeUrl = (url) => url.replace(/\/$/, '');

// Get backend URL from environment or default to localhost instead of 0.0.0.0
const backendUrl = normalizeUrl(process.env.NEXT_PUBLIC_OPENAI_URL || "http://localhost:8000");

function useHandleStreamResponse({
  onChunk,
  onFinish
}) {
  const handleStreamResponse = React.useCallback(
    async (response) => {
      if (response.body) {
        const reader = response.body.getReader();
        if (reader) {
          const decoder = new TextDecoder();
          let content = "";
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              onFinish(content);
              break;
            }
            const chunk = decoder.decode(value, { stream: true });
            content += chunk;
            onChunk(content);
          }
        }
      }
    },
    [onChunk, onFinish]
  );
  return handleStreamResponse;
}

function useUpload() {
  const [loading, setLoading] = React.useState(false);
  const upload = React.useCallback(async (input) => {
    try {
      setLoading(true);
      let response;

      const uploadUrl = `${backendUrl}/api/upload`;
      console.log('Uploading to:', uploadUrl); // Debug log

      if ("file" in input) {
        const formData = new FormData();
        formData.append("file", input.file);
        response = await fetch(uploadUrl, {
          method: "POST",
          body: formData
        });
      } else if ("url" in input) {
        response = await fetch(uploadUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ url: input.url })
        });
      } else if ("base64" in input) {
        response = await fetch(uploadUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ base64: input.base64 })
        });
      } else {
        response = await fetch(uploadUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/octet-stream"
          },
          body: input.buffer
        });
      }

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Upload error response:', errorText); // Debug log
        
        if (response.status === 413) {
          throw new Error("Upload failed: File too large.");
        }
        throw new Error(`Upload failed: ${errorText}`);
      }

      const data = await response.json();
      // Ensure the URL is absolute if it's not already
      const url = data.url.startsWith('http') ? data.url : `${backendUrl}${data.url}`;
      
      return { url, mimeType: data.mimeType || null };
    } catch (uploadError) {
      console.error('Upload error:', uploadError); // Debug log
      if (uploadError instanceof Error) {
        return { error: uploadError.message };
      }
      if (typeof uploadError === "string") {
        return { error: uploadError };
      }
      return { error: "Upload failed" };
    } finally {
      setLoading(false);
    }
  }, []);

  return [upload, { loading }];
}

// Export the backendUrl as well so it can be used consistently across the app
export {
  useHandleStreamResponse,
  useUpload,
  backendUrl,
};