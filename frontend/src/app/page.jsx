"use client";
import React, { useState } from "react";


import { useUpload } from "../utilities/runtime-helpers";

function MainComponent() {
  const [searchQuery, setSearchQuery] = useState("");
  const [showChat, setShowChat] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [messages, setMessages] = useState([]);
  const [upload, { loading }] = useUpload();
  const [images, setImages] = useState([]);
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [isSearchListening, setIsSearchListening] = useState(false);
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setAnalyzing(true);
    const { url, error } = await upload({ file });
    if (error) {
      setError(error);
      setAnalyzing(false);
      return;
    }

    setImages((prev) => [...prev, url]);

    try {
      const response = await fetch("/integrations/gpt-vision/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: "Analyze this histopathology image for cellular structures and potential abnormalities",
                },
                {
                  type: "image_url",
                  image_url: {
                    url,
                  },
                },
              ],
            },
          ],
        }),
      });

      const data = await response.json();
      const analysisText = data.choices[0].message.content;

      setAnalysis(analysisText);
      setMessages((prev) => [
        ...prev,
        { text: "I've uploaded a new image for analysis", sender: "user" },
        { text: analysisText, sender: "assistant" },
      ]);
    } catch (err) {
      setError("Failed to analyze image");
    }

    setAnalyzing(false);
  };

  const handleDataUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setAnalyzing(true);
    const { url, error } = await upload({ file });
    if (error) {
      setError(error);
      setAnalyzing(false);
      return;
    }

    setData((prev) => [...prev, url]);

    try {
      const response = await fetch("/integrations/gpt-vision/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: "Analyze this gene expression data and provide insights about patterns and potential biological significance",
                },
                {
                  type: "image_url",
                  image_url: {
                    url,
                  },
                },
              ],
            },
          ],
        }),
      });

      const data = await response.json();
      const analysisText = data.choices[0].message.content;

      setAnalysis(analysisText);
      setMessages((prev) => [
        ...prev,
        {
          text: "I've uploaded gene expression data for analysis",
          sender: "user",
        },
        { text: analysisText, sender: "assistant" },
      ]);
    } catch (err) {
      setError("Failed to analyze data");
    }

    setAnalyzing(false);
  };

  const handleSendMessage = async (message) => {
    setMessages((prev) => [...prev, { text: message, sender: "user" }]);

    try {
      const response = await fetch("/integrations/gpt-vision/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: message,
                },
                {
                  type: "image_url",
                  image_url: {
                    url: images[images.length - 1] || data[data.length - 1],
                  },
                },
              ],
            },
          ],
        }),
      });

      const data = await response.json();
      const analysisText = data.choices[0].message.content;

      setMessages((prev) => [
        ...prev,
        { text: analysisText, sender: "assistant" },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          text: "Sorry, I couldn't analyze that aspect of the data.",
          sender: "assistant",
        },
      ]);
    }
  };
  const handleAnalyzeWithAI = () => {
    setCurrentPage(2);
    setTimeout(() => {
      setCurrentPage(3);
    }, 2000);
  };
  const handleVoiceInput = () => {
    if ("webkitSpeechRecognition" in window) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setTranscript(transcript);
        handleSendMessage(transcript);
      };

      recognition.onerror = (event) => {
        console.error(event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    }
  };
  const handleSearchVoiceInput = () => {
    if ("webkitSpeechRecognition" in window) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setIsSearchListening(true);
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setSearchQuery(transcript);
      };

      recognition.onerror = (event) => {
        console.error(event.error);
        setIsSearchListening(false);
      };

      recognition.onend = () => {
        setIsSearchListening(false);
      };

      recognition.start();
    }
  };

  const handleSearch = async (query) => {
    try {
      const response = await fetch("/integrations/chat-gpt/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [
            {
              role: "system",
              content:
                "You are a helpful AI assistant that helps users find the right cancer research models based on their search queries.",
            },
            {
              role: "user",
              content: `Find relevant cancer research models for: ${query}`,
            },
          ],
        }),
      });
      const data = await response.json();
    } catch (error) {
      console.error("Error searching models:", error);
    }
  };

  useEffect(() => {
    if (searchQuery) {
      handleSearch(searchQuery);
    }
  }, [searchQuery]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#f8fafc] to-[#e2e8f0]">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="flex items-center">
              <i className="fas fa-dna text-[#6366f1] text-2xl mr-2"></i>
              <i className="fas fa-brain text-[#6366f1] text-2xl"></i>
            </div>
            <h1
              onClick={() => setCurrentPage(1)}
              className="text-2xl font-bold font-inter text-[#1e293b] cursor-pointer hover:text-[#6366f1] transition-colors"
            >
              biotune.ai
            </h1>
          </div>
          <button className="bg-[#6366f1] text-white px-6 py-2 rounded-lg font-inter hover:bg-[#4f46e5] transition-colors">
            Sign In
          </button>
        </div>
      </header>

      {currentPage === 1 ? (
        <div className="flex h-[calc(100vh-80px)]">
          <div className="w-1/2 border-r border-gray-200 p-4 flex flex-col">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  version="1.0"
                  viewBox="0 0 147.288 156.132"
                  className="w-full h-full"
                >
                  <defs>
                    <clipPath clipPathUnits="userSpaceOnUse" id="a">
                      <path d="M1.599 2.159h147.11v156.225H1.6z" />
                    </clipPath>
                  </defs>
                  <path
                    clip-path="url(#a)"
                    d="M84.549 7.875C72.476 6.556 61.203.76 52.049 4.317c-8.355 3.558-10.434 11.993-16.67 19.549-5.837 6.675-16.27 11.992-20.428 19.987-5.437 8.435-4.997 19.069-7.076 27.504C4.118 84.709.76 94.902 4.118 106.016c3.317 10.194 12.512 16.43 17.909 24.425 4.997 7.076 6.676 16.43 11.673 21.747 9.154 6.636 21.267 4.877 32.5 4.437 16.27-.88 35.418.88 49.61-12.872 7.915-7.556 15.39-8.435 21.227-23.986 6.276-15.55-1.24-27.063 1.28-34.179 2.917-8.435 9.553-13.312 9.154-21.307-.84-12.432-4.997-17.31-14.592-28.423-4.996-5.756-7.475-13.312-19.588-23.985-5.836-5.317-17.51-2.679-28.742-3.998z"
                    fill="#e4aa68"
                    fill-rule="evenodd"
                    fill-opacity="1"
                    stroke="none"
                  />
                  <path
                    d="M42.534 80.351c-.44 8.435 7.076 18.19 10.834 27.064 2.918 4.877 10.393 7.995 15.39 12.432 5.837 5.797 9.155 12.873 16.67 12.873 7.915.44 22.067-3.558 28.703-10.634 5.836-8.435 8.755-19.548 9.994-25.784 2.079-12.433-7.476-21.307-9.994-29.303-2.079-4.437-9.155-6.196-14.551-10.633-5.837-4.437-9.595-11.993-16.67-12.433-8.315-.48-18.31 7.996-23.706 11.513-8.755 8.915-16.67 15.99-16.67 24.905z"
                    fill="#d88b31"
                    fill-rule="evenodd"
                    fill-opacity="1"
                    stroke="none"
                  />
                  <path
                    d="M36.698 73.156c-.44 8.475 7.075 18.229 10.833 27.143 2.918 4.877 10.394 7.995 15.39 12.433 5.837 5.756 9.155 12.872 16.67 12.872 7.916.44 22.067-3.558 28.703-10.674 5.837-8.435 8.755-19.548 9.994-25.744 2.08-12.472-7.475-21.347-9.994-29.342-2.078-4.438-9.154-6.236-14.55-10.674-5.837-4.437-9.595-11.993-16.67-12.432-8.316-.48-18.31 7.995-23.706 11.553-8.755 8.874-16.67 15.99-16.67 24.865z"
                    fill="#0094b2"
                    fill-rule="evenodd"
                    fill-opacity="1"
                    stroke="none"
                  />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-lg font-semibold">Hello! 👋</p>
                <p className="text-gray-600">
                  Tell us about your cancer research
                </p>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto mb-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`mb-4 ${
                    msg.sender === "user" ? "text-right" : ""
                  }`}
                >
                  <div
                    className={`inline-block p-3 rounded-lg ${
                      msg.sender === "user"
                        ? "bg-[#6366f1] text-white"
                        : "bg-gray-100"
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>
            <div className="relative flex items-center">
              <input
                type="text"
                placeholder="Type your message..."
                className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#6366f1]"
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === "Enter") {
                    handleSendMessage(e.target.value);
                    setTranscript("");
                  }
                }}
              />
              <button
                onClick={handleVoiceInput}
                className="absolute right-2 p-2 text-gray-500 hover:text-[#6366f1]"
              >
                <i
                  className={`fas ${isListening ? "fa-stop" : "fa-microphone"}`}
                ></i>
              </button>
            </div>
          </div>

          <div className="w-1/2 p-4">
            <div className="mb-4">
              <h2 className="text-xl font-bold mb-2">Images</h2>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
              />
              <label
                htmlFor="image-upload"
                className="block w-full py-2 px-4 text-center bg-[#6366f1] text-white rounded-lg cursor-pointer hover:bg-[#4f46e5] transition-all transform hover:scale-105 disabled:opacity-50"
              >
                {analyzing
                  ? "Analyzing Image..."
                  : loading
                  ? "Uploading..."
                  : "Upload Image"}
              </label>
              {error && <div className="text-red-500 mt-2">{error}</div>}
            </div>
            <div className="grid grid-cols-2 gap-4">
              {images.map((img, idx) => (
                <div key={idx} className="relative group">
                  <img
                    src={img}
                    alt={`Uploaded medical image ${idx + 1}`}
                    className="w-full h-40 object-cover rounded-lg transition-all duration-300 group-hover:brightness-90"
                  />
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      className="bg-[#6366f1] text-white px-4 py-2 rounded-lg hover:bg-[#4f46e5] transition-colors"
                      onClick={() => setCurrentPage(2)}
                    >
                      Analyze with Models →
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8">
              <h2 className="text-xl font-bold mb-2">Gene Expression</h2>
              <input
                type="file"
                accept=".csv,.tsv,.txt"
                onChange={handleDataUpload}
                className="hidden"
                id="data-upload"
              />
              <label
                htmlFor="data-upload"
                className="block w-full py-2 px-4 text-center bg-[#6366f1] text-white rounded-lg cursor-pointer hover:bg-[#4f46e5] transition-all transform hover:scale-105 disabled:opacity-50"
              >
                {analyzing
                  ? "Analyzing Data..."
                  : loading
                  ? "Uploading..."
                  : "Upload Data"}
              </label>
              {data.length > 0 && (
                <div className="mt-4">
                  <div className="bg-gray-100 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">
                      {data.length} data file{data.length !== 1 ? "s" : ""}{" "}
                      uploaded
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : currentPage === 2 ? (
        <div className="relative">
          <button
            onClick={() => setCurrentPage(1)}
            className="absolute top-4 left-4 text-[#6366f1] hover:text-[#4f46e5] transition-colors"
          >
            <i className="fas fa-arrow-left text-2xl"></i>
          </button>
          <div className="flex items-center justify-center h-[calc(100vh-80px)]">
            <div className="text-center">
              <div className="w-16 h-16 mb-4 mx-auto border-4 border-[#6366f1] border-t-transparent rounded-full animate-spin"></div>
              <h2 className="text-2xl font-bold text-[#1e293b] mb-2">
                Analyzing with AI
              </h2>
              <p className="text-gray-600">
                Please wait while we process your images...
              </p>
            </div>
          </div>
        </div>
      ) : (
        <main className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold font-inter text-[#1e293b] mb-4">
              Find the Perfect Model for Your Research
            </h2>
            <div className="max-w-2xl mx-auto relative">
              <input
                type="text"
                placeholder="Search models for cancer biology research..."
                className="w-full px-6 py-4 rounded-xl border border-gray-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#6366f1] font-inter"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button
                onClick={handleSearchVoiceInput}
                className="absolute right-6 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#6366f1] transition-colors"
              >
                <i
                  className={`fas ${
                    isSearchListening ? "fa-stop" : "fa-microphone"
                  }`}
                ></i>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((item) => (
              <div
                key={item}
                className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-bold font-inter text-lg text-[#1e293b]">
                      {item === 1 ? "UNI" : item === 2 ? "CONCH" : "VIRCHOW"}
                    </h3>
                    <p className="text-gray-600 text-sm">
                      {item === 1
                        ? "Universal Histopathology Model"
                        : item === 2
                        ? "Contextual Histopathology Analysis"
                        : "Advanced Tissue Classification"}
                    </p>
                  </div>
                  <span className="bg-[#f1f5f9] text-[#475569] text-xs px-3 py-1 rounded-full">
                    {item === 1 ? "New" : item === 2 ? "Popular" : "Stable"}
                  </span>
                </div>
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <i className="fas fa-microscope w-5"></i>
                    <span>
                      {item === 1
                        ? "95% Accuracy on TCGA dataset"
                        : item === 2
                        ? "98% Accuracy on PathAI dataset"
                        : "97% Accuracy on CAMELYON dataset"}
                    </span>
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <i className="fas fa-clock w-5"></i>
                    <span>
                      Processing time:{" "}
                      {item === 1 ? "~1" : item === 2 ? "~2" : "~1.5"} hours
                    </span>
                  </div>
                </div>
                <button className="w-full bg-[#6366f1] text-white py-2 rounded-lg font-inter hover:bg-[#4f46e5] transition-colors">
                  Explore Model
                </button>
              </div>
            ))}
          </div>
        </main>
      )}

      {currentPage === 1 && (
        <div className="fixed bottom-8 right-8 flex gap-4">
          <button
            onClick={handleAnalyzeWithAI}
            className="bg-[#6366f1] text-white px-6 py-3 rounded-full shadow-lg hover:bg-[#4f46e5] transition-all transform hover:scale-105 flex items-center justify-center"
          >
            <span className="mr-2">Analyze with AI</span>
            <i className="fas fa-robot"></i>
          </button>
        </div>
      )}
    </div>
  );
}

export default MainComponent;