const inputText = document.getElementById("inputText");
const methodSelect = document.getElementById("method");
const summaryLengthSelect = document.getElementById("summaryLength");
const generateButton = document.getElementById("generateButton");
const statusMessage = document.getElementById("statusMessage");
const outputSection = document.getElementById("outputSection");
const selectedMeta = document.getElementById("selectedMeta");

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

generateButton.addEventListener("click", summarize);

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
    try {
        const data = await mockBackendResponse(payload);
        renderOutput(payload, data);
    } catch (error) {
        statusMessage.textContent = "Unable to generate summary right now. Please try again.";
        hideOutputs();
        console.error(error);
    }
}

async function mockBackendResponse(payload) {
    await delay(350);

    const preview = shortenText(payload.text, 240);
    const summaryPrefix = payload.summary_length.charAt(0).toUpperCase() + payload.summary_length.slice(1);

    const mockResponse = {
        transformer: `${summaryPrefix} transformer summary: ${preview} This version is phrased more fluently and focuses on the overall narrative.`,
        nltk: `${summaryPrefix} NLTK summary: ${preview} This version highlights frequent and important sentences from the source text.`,
        transformer_time: 0.52,
        nltk_time: 0.21,
    };

    if (payload.method === "transformer") {
        return {
            transformer: mockResponse.transformer,
            transformer_time: mockResponse.transformer_time,
        };
    }

    if (payload.method === "nltk") {
        return {
            nltk: mockResponse.nltk,
            nltk_time: mockResponse.nltk_time,
        };
    }

    return mockResponse;
}

function renderOutput(payload, data) {
    outputSection.classList.remove("hidden");
    originalOutput.textContent = payload.text;
    selectedMeta.textContent = `${getMethodLabel(payload.method)} | ${capitalize(payload.summary_length)}`;

    if (payload.method === "compare") {
        singleSummaryBlock.classList.add("hidden");
        compareGrid.classList.remove("hidden");

        transformerOutput.textContent = data.transformer;
        nltkOutput.textContent = data.nltk;
        transformerTiming.textContent = `⏱ ${formatTime(data.transformer_time)}`;
        nltkTiming.textContent = `⏱ ${formatTime(data.nltk_time)}`;
        return;
    }

    compareGrid.classList.add("hidden");
    singleSummaryBlock.classList.remove("hidden");

    if (payload.method === "transformer") {
        singleSummaryTitle.textContent = "Transformer Summary";
        singleSummaryText.textContent = data.transformer;
        singleTiming.textContent = `⏱ ${formatTime(data.transformer_time)}`;
    } else {
        singleSummaryTitle.textContent = "NLTK Summary";
        singleSummaryText.textContent = data.nltk;
        singleTiming.textContent = `⏱ ${formatTime(data.nltk_time)}`;
    }
}

function hideOutputs() {
    outputSection.classList.add("hidden");
    singleSummaryBlock.classList.add("hidden");
    compareGrid.classList.add("hidden");
}

function resetStatus() {
    statusMessage.textContent = "";
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

function shortenText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }

    return `${text.slice(0, maxLength).trim()}...`;
}

function delay(milliseconds) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

// Placeholder for future API integration:
// async function fetchSummary(payload) {
//     const response = await fetch("/api/summarize", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify(payload),
//     });
//     return response.json();
// }
