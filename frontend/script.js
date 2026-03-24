const inputText = document.getElementById("inputText");
const fileInput = document.getElementById("fileInput");
const methodSelect = document.getElementById("method");
const summaryLengthSelect = document.getElementById("summaryLength");
const generateButton = document.getElementById("generateButton");
const copySummaryButton = document.getElementById("copySummaryButton");
const downloadSummaryButton = document.getElementById("downloadSummaryButton");
const loaderBox = document.getElementById("loaderBox");
const loaderText = document.getElementById("loaderText");
const statusMessage = document.getElementById("statusMessage");
const outputSection = document.getElementById("outputSection");
const selectedMeta = document.getElementById("selectedMeta");
const summaryToolbar = document.getElementById("summaryToolbar");
const compressionInfo = document.getElementById("compressionInfo");

const singleSummaryBlock = document.getElementById("singleSummaryBlock");
const singleSummaryTitle = document.getElementById("singleSummaryTitle");
const singleSummaryText = document.getElementById("singleSummaryText");
const singleTiming = document.getElementById("singleTiming");

const compareGrid = document.getElementById("compareGrid");
const originalOutput = document.getElementById("originalOutput");
const transformerOutput = document.getElementById("transformerOutput");
const nltkOutput = document.getElementById("nltkOutput");
const transformerTiming = document.getElementById("transformerTiming");
const nltkTiming = document.getElementById("nltkTiming");
const transformerCompression = document.getElementById("transformerCompression");
const nltkCompression = document.getElementById("nltkCompression");

const API_BASE_URL = "http://127.0.0.1:8000";

let loaderIntervalId = null;
let latestSummaryText = "";

generateButton.addEventListener("click", summarize);
fileInput.addEventListener("change", handleFileUpload);
copySummaryButton.addEventListener("click", copySummary);
downloadSummaryButton.addEventListener("click", downloadSummary);

async function handleFileUpload(event) {
    const selectedFile = event.target.files[0];

    if (!selectedFile) {
        return;
    }

    resetStatus();
    setLoadingState(true, "🧸💭 Loading your file");

    try {
        const formData = new FormData();
        formData.append("file", selectedFile);

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "We could not read that file.");
        }

        inputText.value = data.text;
        statusMessage.textContent = "📄 File loaded successfully";
    } catch (error) {
        statusMessage.textContent = error.message || "Unable to load the selected file.";
    } finally {
        setLoadingState(false);
    }
}

function summarize() {
    const originalText = inputText.value.trim();
    const method = methodSelect.value;
    const summaryLength = summaryLengthSelect.value;

    resetStatus();

    if (!originalText) {
        statusMessage.textContent = "Please enter some text before generating a summary.";
        hideOutputs();
        return;
    }

    const payload = {
        text: originalText,
        method,
        summary_length: summaryLength,
    };

    void fetchSummary(payload);
}

async function fetchSummary(payload) {
    setLoadingState(true, "🐻✨ Generating your summary");

    try {
        const endpoint = payload.method === "compare" ? "/compare" : "/summarize";
        const requestBody =
            payload.method === "compare"
                ? {
                      text: payload.text,
                      summary_length: payload.summary_length,
                  }
                : payload;

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestBody),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "The server could not process your request.");
        }

        renderOutput(payload, data);
    } catch (error) {
        statusMessage.textContent =
            error.message || "Unable to generate summary right now. Please try again.";
        hideOutputs();
        console.error(error);
    } finally {
        setLoadingState(false);
    }
}

function renderOutput(payload, data) {
    outputSection.classList.remove("hidden");
    summaryToolbar.classList.remove("hidden");
    originalOutput.textContent = payload.text;
    selectedMeta.textContent = `${getMethodLabel(payload.method)} | ${capitalize(payload.summary_length)}`;

    if (payload.method === "compare") {
        singleSummaryBlock.classList.add("hidden");
        compareGrid.classList.remove("hidden");
        compressionInfo.classList.add("hidden");

        transformerOutput.textContent = data.transformer;
        nltkOutput.textContent = data.nltk;
        transformerTiming.textContent = `Time: ${formatTime(data.transformer_time)}`;
        nltkTiming.textContent = `Time: ${formatTime(data.nltk_time)}`;
        transformerCompression.textContent = getCompressionText(payload.text, data.transformer);
        nltkCompression.textContent = getCompressionText(payload.text, data.nltk);
        latestSummaryText = buildCompareSummaryText(data);
        return;
    }

    compareGrid.classList.add("hidden");
    singleSummaryBlock.classList.remove("hidden");
    compressionInfo.classList.remove("hidden");

    if (payload.method === "transformer") {
        singleSummaryTitle.textContent = "Transformer Summary";
    } else {
        singleSummaryTitle.textContent = "NLTK Summary";
    }

    singleSummaryText.textContent = data.summary;
    singleTiming.textContent = `Time: ${formatTime(data.time)}`;
    compressionInfo.textContent = getCompressionText(payload.text, data.summary);
    latestSummaryText = data.summary;
}

function hideOutputs() {
    outputSection.classList.add("hidden");
    singleSummaryBlock.classList.add("hidden");
    compareGrid.classList.add("hidden");
    summaryToolbar.classList.add("hidden");
    compressionInfo.classList.add("hidden");
    latestSummaryText = "";
}

function resetStatus() {
    statusMessage.textContent = "";
}

function setLoadingState(isLoading, baseText = "🧸💭 Thinking") {
    generateButton.disabled = isLoading;
    generateButton.textContent = isLoading ? "Working..." : "Generate Summary";

    if (isLoading) {
        loaderBox.classList.remove("hidden");
        startLoaderAnimation(baseText);
        return;
    }

    loaderBox.classList.add("hidden");
    stopLoaderAnimation();
}

function startLoaderAnimation(baseText) {
    stopLoaderAnimation();

    const frames = [".", "..", "..."];
    let frameIndex = 0;

    loaderText.textContent = `${baseText}${frames[frameIndex]}`;
    loaderIntervalId = window.setInterval(() => {
        frameIndex = (frameIndex + 1) % frames.length;
        loaderText.textContent = `${baseText}${frames[frameIndex]}`;
    }, 450);
}

function stopLoaderAnimation() {
    if (loaderIntervalId !== null) {
        window.clearInterval(loaderIntervalId);
        loaderIntervalId = null;
    }
}

async function copySummary() {
    if (!latestSummaryText) {
        statusMessage.textContent = "Generate a summary before copying it.";
        return;
    }

    try {
        await navigator.clipboard.writeText(latestSummaryText);
        statusMessage.textContent = "📋 Summary copied to clipboard";
    } catch (error) {
        statusMessage.textContent = "Unable to copy the summary right now.";
    }
}

function downloadSummary() {
    if (!latestSummaryText) {
        statusMessage.textContent = "Generate a summary before downloading it.";
        return;
    }

    const blob = new Blob([latestSummaryText], { type: "text/plain;charset=utf-8" });
    const downloadUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = "summary.txt";
    link.click();
    URL.revokeObjectURL(downloadUrl);
    statusMessage.textContent = "⬇️ Summary downloaded";
}

function buildCompareSummaryText(data) {
    return [
        "Transformer Summary",
        data.transformer,
        "",
        "NLTK Summary",
        data.nltk,
    ].join("\n");
}

function getCompressionText(originalText, summaryText) {
    const originalWords = countWords(originalText);
    const summaryWords = countWords(summaryText);

    if (originalWords === 0) {
        return "Original: 0 words -> Summary: 0 words (0% reduction)";
    }

    const reduction = Math.max(0, ((originalWords - summaryWords) / originalWords) * 100);
    return `Original: ${originalWords} words -> Summary: ${summaryWords} words (${Math.round(reduction)}% reduction)`;
}

function countWords(text) {
    if (!text.trim()) {
        return 0;
    }

    return text.trim().split(/\s+/).length;
}

function getMethodLabel(method) {
    const labels = {
        transformer: "Transformer",
        nltk: "NLTK",
        compare: "Compare Both",
    };

    return labels[method] || "Unknown";
}

function capitalize(value) {
    return value.charAt(0).toUpperCase() + value.slice(1);
}

function formatTime(timeInSeconds) {
    return `${Number(timeInSeconds).toFixed(2)} seconds`;
}
