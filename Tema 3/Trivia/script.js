const questions = [
    {
        question: "In ce an suntem?",
        options: ["2021", "2022", "2023", "2024"],
        correctAnswer: "2024"
    },
    {
        question: "In ce limbaj de programare este scris acest quiz?",
        options: ["C++", "JavaScript", "Python", "Java"],
        correctAnswer: "JavaScript"
    },
    {
        question: "Care este capitala Romaniei?",
        options: ["Bucuresti", "Cluj-Napoca", "Timisoara", "Iasi"],
        correctAnswer: "Bucuresti"
    }
];

let currentQuestionIndex = 0;
let score = 0;

function startGame() {
    displayQuestion();
}

function displayQuestion() {
    const questionContainer = document.getElementById("question-container");
    const optionsContainer = document.getElementById("options-container");
    const nextBtn = document.getElementById("next-btn");

    questionContainer.innerHTML = questions[currentQuestionIndex].question;
    optionsContainer.innerHTML = "";

    questions[currentQuestionIndex].options.forEach((option, index) => {
        const optionBtn = document.createElement("button");
        optionBtn.textContent = option;
        optionBtn.addEventListener("click", () => checkAnswer(optionBtn, option));
        optionsContainer.appendChild(optionBtn);
    });

    nextBtn.classList.add("hidden");
}

function checkAnswer(selectedBtn, userAnswer) {
    const correctAnswer = questions[currentQuestionIndex].correctAnswer;
    const nextBtn = document.getElementById("next-btn");

    document.querySelectorAll("#options-container button").forEach(btn => btn.removeEventListener("click", () => {}));

    if (userAnswer === correctAnswer) {
        score++;
        selectedBtn.style.backgroundColor = "#28a745";
        document.getElementById("question-container").innerHTML = "Correct Answer";
    } else {
        selectedBtn.style.backgroundColor = "#dc3545";
        document.getElementById("question-container").innerHTML = "Wrong Answer";

        document.querySelectorAll("#options-container button").forEach(btn => {
            if (btn.textContent === correctAnswer) {
                btn.style.backgroundColor = "#28a745";
            }
        });
    }

    document.getElementById("score").textContent = "Score: " + score;
    nextBtn.classList.remove("hidden");
}



function nextQuestion() {
    document.querySelectorAll("#options-container button").forEach(btn => btn.style.backgroundColor = "#007bff");

    currentQuestionIndex++;

    if (currentQuestionIndex < questions.length) {
        displayQuestion();
    } else {
        endGame();
    }
}

function endGame() {
    const quizContainer = document.getElementById("quiz-container");
    quizContainer.innerHTML = `<h1>Game Over</h1><p>Your final score is: ${score}</p>`;
}

startGame();
