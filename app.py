import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌깨기 게임",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 벽돌깨기 게임")
st.write("키보드 ← → 또는 A / D 키로 막대를 움직이세요.")

game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">

<style>
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        padding: 0;
        background: #111827;
        color: white;
        font-family: Arial, sans-serif;
        text-align: center;
    }

    #game-wrapper {
        width: 100%;
        max-width: 850px;
        margin: 0 auto;
    }

    #info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
        font-size: 18px;
        font-weight: bold;
    }

    #game-container {
        width: 100%;
        background: #020617;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 0 25px rgba(0,0,0,0.5);
    }

    canvas {
        display: block;
        width: 100%;
        height: auto;
        background: linear-gradient(
            180deg,
            #0f172a,
            #020617
        );
        border-radius: 8px;
    }

    button {
        margin: 10px 5px;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        background: #2563eb;
        color: white;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
    }

    button:hover {
        background: #1d4ed8;
    }

    #message {
        min-height: 28px;
        font-size: 20px;
        font-weight: bold;
        color: #facc15;
    }
</style>
</head>

<body>

<div id="game-wrapper">

    <div id="info">
        <div>점수: <span id="score">0</span></div>
        <div>목숨: <span id="lives">3</span></div>
        <div>레벨: <span id="level">1</span></div>
    </div>

    <div id="game-container">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
    </div>

    <button onclick="startGame()">게임 시작</button>
    <button onclick="restartGame()">다시 시작</button>

    <div id="message">
        게임 시작 버튼을 눌러주세요!
    </div>

</div>

<script>

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;

/* =========================
   게임 설정
========================= */

const paddle = {
    width: 120,
    height: 15,
    x: WIDTH / 2 - 60,
    y: HEIGHT - 40,
    speed: 8,
    dx: 0
};

const ball = {
    x: WIDTH / 2,
    y: HEIGHT - 60,
    radius: 9,
    dx: 4,
    dy: -4
};

const brick = {
    rows: 5,
    cols: 10,
    width: 70,
    height: 25,
    gap: 8,
    top: 70,
    left: 45
};

let bricks = [];

let score = 0;
let lives = 3;
let level = 1;

let gameRunning = false;
let animationId = null;

let keys = {
    left: false,
    right: false
};


/* =========================
   벽돌 생성
========================= */

function createBricks() {

    bricks = [];

    for (let row = 0; row < brick.rows; row++) {

        for (let col = 0; col < brick.cols; col++) {

            bricks.push({
                x: brick.left + col * (brick.width + brick.gap),
                y: brick.top + row * (brick.height + brick.gap),

                width: brick.width,
                height: brick.height,

                alive: true,

                color: getBrickColor(row)
            });
        }
    }
}


/* =========================
   벽돌 색상
========================= */

function getBrickColor(row) {

    const colors = [
        "#ef4444",
        "#f97316",
        "#eab308",
        "#22c55e",
        "#3b82f6"
    ];

    return colors[row % colors.length];
}


/* =========================
   화면 그리기
========================= */

function draw() {

    ctx.clearRect(0, 0, WIDTH, HEIGHT);

    drawBricks();
    drawPaddle();
    drawBall();

}


/* =========================
   벽돌 그리기
========================= */

function drawBricks() {

    bricks.forEach(b => {

        if (!b.alive) {
            return;
        }

        ctx.fillStyle = b.color;

        ctx.beginPath();

        ctx.roundRect(
            b.x,
            b.y,
            b.width,
            b.height,
            5
        );

        ctx.fill();

        ctx.strokeStyle = "rgba(255,255,255,0.2)";
        ctx.stroke();

    });
}


/* =========================
   패들 그리기
========================= */

function drawPaddle() {

    ctx.fillStyle = "#06b6d4";

    ctx.beginPath();

    ctx.roundRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height,
        8
    );

    ctx.fill();
}


/* =========================
   공 그리기
========================= */

function drawBall() {

    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        ball.radius,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = "#ffffff";

    ctx.shadowColor = "#38bdf8";
    ctx.shadowBlur = 15;

    ctx.fill();

    ctx.shadowBlur = 0;
}


/* =========================
   공 이동
========================= */

function moveBall() {

    ball.x += ball.dx;
    ball.y += ball.dy;


    /* 왼쪽 / 오른쪽 벽 */

    if (
        ball.x + ball.radius >= WIDTH ||
        ball.x - ball.radius <= 0
    ) {
        ball.dx *= -1;
    }


    /* 위쪽 벽 */

    if (ball.y - ball.radius <= 0) {
        ball.dy *= -1;
    }


    /* 아래쪽 */

    if (ball.y - ball.radius > HEIGHT) {

        loseLife();

        return;
    }


    /* 패들 충돌 */

    if (
        ball.y + ball.radius >= paddle.y &&
        ball.y - ball.radius <= paddle.y + paddle.height &&
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width &&
        ball.dy > 0
    ) {

        ball.dy *= -1;

        /*
           패들의 어느 부분에 맞았는지에 따라
           공의 방향을 바꿔줍니다.
        */

        const hitPosition =
            (ball.x - paddle.x) / paddle.width;

        ball.dx = (hitPosition - 0.5) * 10;

    }


    /* 벽돌 충돌 */

    bricks.forEach(b => {

        if (!b.alive) {
            return;
        }

        if (
            ball.x + ball.radius > b.x &&
            ball.x - ball.radius < b.x + b.width &&
            ball.y + ball.radius > b.y &&
            ball.y - ball.radius < b.y + b.height
        ) {

            b.alive = false;

            ball.dy *= -1;

            score += 10;

            updateUI();

        }

    });


    /* 모든 벽돌 제거 */

    const remaining =
        bricks.filter(b => b.alive).length;

    if (remaining === 0) {

        nextLevel();
    }

}


/* =========================
   패들 이동
========================= */

function movePaddle() {

    if (keys.left) {
        paddle.x -= paddle.speed;
    }

    if (keys.right) {
        paddle.x += paddle.speed;
    }


    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (paddle.x + paddle.width > WIDTH) {
        paddle.x = WIDTH - paddle.width;
    }

}


/* =========================
   목숨 감소
========================= */

function loseLife() {

    lives--;

    updateUI();

    if (lives <= 0) {

        gameOver();

        return;
    }


    resetBall();

}


/* =========================
   공 초기화
========================= */

function resetBall() {

    ball.x = WIDTH / 2;
    ball.y = HEIGHT - 60;

    ball.dx = 4 * (Math.random() > 0.5 ? 1 : -1);
    ball.dy = -4;

    paddle.x = WIDTH / 2 - paddle.width / 2;

}


/* =========================
   다음 레벨
========================= */

function nextLevel() {

    level++;

    document.getElementById("message").textContent =
        "🎉 레벨 클리어!";

    createBricks();

    ball.dx *= 1.1;
    ball.dy *= 1.1;

    updateUI();

}


/* =========================
   게임 시작
========================= */

function startGame() {

    if (gameRunning) {
        return;
    }

    gameRunning = true;

    document.getElementById("message").textContent =
        "🔥 게임 진행 중!";

    gameLoop();

}


/* =========================
   게임 재시작
========================= */

function restartGame() {

    score = 0;
    lives = 3;
    level = 1;

    paddle.x = WIDTH / 2 - paddle.width / 2;

    ball.x = WIDTH / 2;
    ball.y = HEIGHT - 60;

    ball.dx = 4;
    ball.dy = -4;

    createBricks();

    gameRunning = true;

    document.getElementById("message").textContent =
        "🔥 게임을 다시 시작합니다!";

    updateUI();

    cancelAnimationFrame(animationId);

    gameLoop();

}


/* =========================
   게임 오버
========================= */

function gameOver() {

    gameRunning = false;

    document.getElementById("message").textContent =
        "💀 게임 오버! 다시 시작해보세요.";

}


/* =========================
   화면 UI 업데이트
========================= */

function updateUI() {

    document.getElementById("score").textContent =
        score;

    document.getElementById("lives").textContent =
        lives;

    document.getElementById("level").textContent =
        level;

}


/* =========================
   게임 루프
========================= */

function gameLoop() {

    if (!gameRunning) {
        draw();
        return;
    }

    movePaddle();
    moveBall();

    draw();

    animationId =
        requestAnimationFrame(gameLoop);

}


/* =========================
   키보드 입력
========================= */

document.addEventListener("keydown", function(event) {

    if (
        event.key === "ArrowLeft" ||
        event.key.toLowerCase() === "a"
    ) {

        keys.left = true;

        event.preventDefault();
    }


    if (
        event.key === "ArrowRight" ||
        event.key.toLowerCase() === "d"
    ) {

        keys.right = true;

        event.preventDefault();
    }

});


document.addEventListener("keyup", function(event) {

    if (
        event.key === "ArrowLeft" ||
        event.key.toLowerCase() === "a"
    ) {

        keys.left = false;
    }


    if (
        event.key === "ArrowRight" ||
        event.key.toLowerCase() === "d"
    ) {

        keys.right = false;
    }

});


/* =========================
   마우스 조작
========================= */

canvas.addEventListener("mousemove", function(event) {

    const rect = canvas.getBoundingClientRect();

    const scaleX = WIDTH / rect.width;

    const mouseX =
        (event.clientX - rect.left) * scaleX;

    paddle.x =
        mouseX - paddle.width / 2;


    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (paddle.x + paddle.width > WIDTH) {
        paddle.x = WIDTH - paddle.width;
    }

});


/* =========================
   모바일 터치 조작
========================= */

canvas.addEventListener("touchmove", function(event) {

    event.preventDefault();

    const rect = canvas.getBoundingClientRect();

    const scaleX = WIDTH / rect.width;

    const touchX =
        (event.touches[0].clientX - rect.left) * scaleX;

    paddle.x =
        touchX - paddle.width / 2;


    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (paddle.x + paddle.width > WIDTH) {
        paddle.x = WIDTH - paddle.width;
    }

}, { passive: false });


/* =========================
   초기화
========================= */

createBricks();
updateUI();
draw();

</script>

</body>
</html>
"""

components.html(
    game_html,
    height=720,
    scrolling=False
)
