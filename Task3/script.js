// Game setup
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const msg = document.getElementById("message");
const scoreEl = document.getElementById("bestScore");
const resetBtn = document.getElementById("resetBtn");
const screenshotBtn = document.getElementById("screenshotBtn");

// Audio
const sounds = {
    draw: document.getElementById("drawSound"),
    success: document.getElementById("successSound"),
    fail: document.getElementById("failSound")
};

let isDrawing = false;
let myPath = [];
let centerDot = {};
let bestScore = parseFloat(sessionStorage.getItem("bestScore")) || 0;
let lastScore = 0;
scoreEl.textContent = bestScore.toFixed(2);

// Make canvas responsive and draw the dot
function setupCanvas() {
    canvas.width = Math.min(window.innerWidth - 40, 500);
    canvas.height = Math.min(window.innerHeight * 0.6, 500);
    centerDot = { x: canvas.width / 2, y: canvas.height / 2 };
    drawCenterDot();
}
window.addEventListener('resize', setupCanvas);
setupCanvas();

// Drawing functions
function getCoords(e) {
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { x: clientX - rect.left, y: clientY - rect.top };
}

function beginDraw(e) {
    e.preventDefault();
    isDrawing = true;
    myPath = [getCoords(e)];
    playAudio(sounds.draw);
}

function continueDraw(e) {
    if (!isDrawing) return;
    e.preventDefault();
    myPath.push(getCoords(e));
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawMyPath();
    drawCenterDot();
}

function endDraw() {
    if (!isDrawing) return;
    isDrawing = false;
    sounds.draw.pause();
    if (myPath.length > 5) {
        evaluate();
    } else {
        resetGame();
    }
}

// Visuals
function drawCenterDot() {
    ctx.beginPath();
    ctx.arc(centerDot.x, centerDot.y, 5, 0, Math.PI * 2);
    ctx.fillStyle = "red";
    ctx.fill();
}

function drawMyPath() {
    ctx.beginPath();
    ctx.moveTo(myPath[0].x, myPath[0].y);
    myPath.forEach(p => ctx.lineTo(p.x, p.y));
    ctx.strokeStyle = "#4a90e2";
    ctx.lineWidth = 3;
    ctx.stroke();
}

// Score evaluation
function evaluate() {
    ctx.beginPath();
    ctx.moveTo(myPath[0].x, myPath[0].y);
    myPath.forEach(p => ctx.lineTo(p.x, p.y));
    ctx.closePath();

    if (!ctx.isPointInPath(centerDot.x, centerDot.y)) {
        msg.textContent = "❌ Not a circle!";
        lastScore = 0;
        playAudio(sounds.fail);
        return;
    }

    const distances = myPath.map(p => Math.hypot(p.x - centerDot.x, p.y - centerDot.y));
    const avg = distances.reduce((sum, d) => sum + d, 0) / distances.length;
    const variance = distances.reduce((sum, d) => sum + (d - avg) ** 2, 0) / distances.length;
    lastScore = Math.max(0, 100 - Math.sqrt(variance));

    msg.textContent = `✅ Score: ${lastScore.toFixed(2)}`;
    if (lastScore > bestScore) {
        bestScore = lastScore;
        sessionStorage.setItem("bestScore", bestScore.toFixed(2));
        scoreEl.textContent = bestScore.toFixed(2);
        playAudio(sounds.success);
    }
}

function resetGame() {
    myPath = [];
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawCenterDot();
    msg.textContent = "Draw a circle around the red dot.";
    lastScore = 0;
}

// Button actions
resetBtn.addEventListener("click", resetGame);
screenshotBtn.addEventListener("click", takeScreenshot);

function takeScreenshot() {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height + 100;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.fillStyle = '#000';
    tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
    tempCtx.drawImage(canvas, 0, 0);
    tempCtx.font = 'bold 24px Roboto';
    tempCtx.fillStyle = '#fff';
    tempCtx.textAlign = 'center';
    tempCtx.fillText(`Score: ${lastScore.toFixed(2)}`, tempCanvas.width / 2, tempCanvas.height - 50);
    const link = document.createElement("a");
    link.download = "circle_score.png";
    link.href = tempCanvas.toDataURL("image/png");
    link.click();
}

// Helper functions for sound
function playAudio(audio) {
    audio.currentTime = 0;
    audio.play().catch(e => console.error("Audio failed:", e));
}

// Event listeners
canvas.addEventListener("mousedown", beginDraw);
canvas.addEventListener("mousemove", continueDraw);
canvas.addEventListener("mouseup", endDraw);
canvas.addEventListener("mouseleave", endDraw);
canvas.addEventListener("touchstart", beginDraw, { passive: false });
canvas.addEventListener("touchmove", continueDraw, { passive: false });
canvas.addEventListener("touchend", endDraw);

// Initial setup
drawCenterDot();
