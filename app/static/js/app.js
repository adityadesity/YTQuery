
const API_BASE = "";

// Application state
let videos = [];
let selectedVideoId = null;
let isProcessing = false;


// DOM elements
const videoUrlInput = document.getElementById("video-url");
const ingestBtn = document.getElementById("ingest-btn");
const ingestStatus = document.getElementById("ingest-status");

const videoList = document.getElementById("video-list");

const chatBox = document.getElementById("chat-box");
const questionInput = document.getElementById("question");
const sendBtn = document.getElementById("send-btn");

const selectedVideoTitle = document.getElementById(
    "selected-video-title"
);

const selectedVideoStatus = document.getElementById(
    "selected-video-status"
);


// -----------------------------
// INGEST VIDEO
// -----------------------------

ingestBtn.addEventListener("click", ingestVideo);

async function ingestVideo() {

    const url = videoUrlInput.value.trim();

    if (!url) {
        ingestStatus.textContent = "Please enter a YouTube URL.";
        return;
    }

    if (isProcessing) return;

    setProcessing(true);
    ingestStatus.textContent = "Fetching transcript and generating embeddings...";

    try {

        const response = await fetch(`${API_BASE}/videos/ingest`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Ingestion failed.");
        }

        if (data.status === "already_ingested") {
            ingestStatus.textContent = "This video is already ingested.";
        } else {
            ingestStatus.textContent =
                `Successfully ingested ${data.total_chunks} chunks.`;
        }

        // Add video to local list if not already present
        const existingVideo = videos.find(
            video => video.video_id === data.video_id
        );

        if (!existingVideo) {
            videos.push({
                video_id: data.video_id,
                title: `YouTube Video (${data.video_id})`
            });
        }

        renderVideoList();
        selectVideo(data.video_id);

        videoUrlInput.value = "";

    } catch (error) {

        ingestStatus.textContent = error.message;

    } finally {
        setProcessing(false);
    }
}


// -----------------------------
// RENDER VIDEO LIST
// -----------------------------

function renderVideoList() {

    videoList.innerHTML = "";

    if (videos.length === 0) {
        videoList.innerHTML =
            '<p class="empty-state">No videos loaded yet.</p>';
        return;
    }

    videos.forEach(video => {

        const item = document.createElement("div");

        item.className = "video-item";

        if (video.video_id === selectedVideoId) {
            item.classList.add("active");
        }

        const name = document.createElement("span");
        name.className = "video-name";
        name.textContent = video.title;

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "delete-btn";
        deleteBtn.textContent = "×";
        deleteBtn.title = "Delete video";

        deleteBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            deleteVideo(video.video_id);
        });

        item.appendChild(name);
        item.appendChild(deleteBtn);

        item.addEventListener("click", () => {
            selectVideo(video.video_id);
        });

        videoList.appendChild(item);
    });
}


// -----------------------------
// SELECT VIDEO
// -----------------------------

function selectVideo(videoId) {

    selectedVideoId = videoId;

    const video = videos.find(
        item => item.video_id === videoId
    );

    if (!video) return;

    selectedVideoTitle.textContent = video.title;
    selectedVideoStatus.textContent = "Ready to answer your questions.";

    questionInput.disabled = false;
    sendBtn.disabled = false;

    // Clear previous conversation when switching videos
    chatBox.innerHTML = "";

    addMessage(
        "bot",
        "Video selected! Ask me anything about its content."
    );

    renderVideoList();
}


// -----------------------------
// CHAT
// -----------------------------

sendBtn.addEventListener("click", sendMessage);

questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        sendMessage();
    }
});

async function sendMessage() {

    const question = questionInput.value.trim();

    if (!question || !selectedVideoId || isProcessing) {
        return;
    }

    addMessage("user", question);

    questionInput.value = "";

    setProcessing(true);

    const loadingMessage = addMessage(
        "bot",
        "Thinking..."
    );

    try {

        const response = await fetch(`${API_BASE}/chat/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                video_id: selectedVideoId,
                question: question
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Chat request failed.");
        }

        loadingMessage.textContent = data.answer;

    } catch (error) {

        loadingMessage.textContent = `Error: ${error.message}`;

    } finally {
        setProcessing(false);
        questionInput.focus();
    }
}


// -----------------------------
// ADD CHAT MESSAGE
// -----------------------------

function addMessage(type, text) {

    const message = document.createElement("div");

    message.className = type === "user"
        ? "message user-message"
        : "message bot-message";

    message.textContent = text;

    chatBox.appendChild(message);

    chatBox.scrollTop = chatBox.scrollHeight;

    return message;
}


// -----------------------------
// DELETE VIDEO
// -----------------------------

async function deleteVideo(videoId) {

    if (isProcessing) return;

    const confirmed = confirm(
        "Are you sure you want to delete this video's data?"
    );

    if (!confirmed) return;

    setProcessing(true);

    try {

        const response = await fetch(
            `${API_BASE}/videos/${encodeURIComponent(videoId)}`,
            {
                method: "DELETE"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Deletion failed.");
        }

        videos = videos.filter(
            video => video.video_id !== videoId
        );

        if (selectedVideoId === videoId) {

            selectedVideoId = null;

            selectedVideoTitle.textContent = "Welcome to TubeQuery";
            selectedVideoStatus.textContent =
                "Select or ingest a video to get started.";

            questionInput.disabled = true;
            sendBtn.disabled = true;

            chatBox.innerHTML = `
                <div class="welcome-message">
                    <h1>Chat with your videos.</h1>
                    <p>Select a video to start asking questions.</p>
                </div>
            `;
        }

        renderVideoList();

    } catch (error) {

        alert(error.message);

    } finally {
        setProcessing(false);
    }
}


// -----------------------------
// PROCESSING STATE
// -----------------------------

function setProcessing(value) {

    isProcessing = value;

    ingestBtn.disabled = value;
    sendBtn.disabled = value || !selectedVideoId;
    questionInput.disabled = value || !selectedVideoId;
}
