let modalProblems = [];
let modalCurrentIndex = 0;
let modalCorrectCount = 0;
let modalWrongCount = 0;
let isSubmittingModalAnswer = false;

function isWordProblem(problem) {
    if (!problem) {
        return false;
    }

    const problemType = problem.type || '';
    const questionText = problem.question || '';
    return problemType.includes('应用题') || questionText.length > 24;
}

function updateModalProblemPresentation(problem) {
    const questionElement = document.getElementById('modal-question');
    const containerElement = document.querySelector('#modal-practice-section .problem-container');
    const wordProblem = isWordProblem(problem);

    questionElement.classList.toggle('word-problem', wordProblem);
    containerElement.classList.toggle('word-problem', wordProblem);
}

function loadSessionBanner() {
    fetch('/api/session_state')
        .then((res) => res.json())
        .then((data) => {
            if (!data.success || !data.logged_in) {
                return;
            }

            const selection = data.selection || {};
            document.getElementById('banner-subject').textContent = selection.subject || '未选择';
            document.getElementById('banner-grade').textContent = selection.grade || '未选择';
            document.getElementById('banner-project').textContent = selection.project || '未选择';
        });
}

function loadWrongProblems() {
    fetch('/api/get_wrong_problems')
        .then((res) => res.json())
        .then((data) => {
            if (!data.success) {
                alert(data.message || '加载失败');
                if (data.message === '请先登录') {
                    location.href = '/';
                }
                return;
            }

            displayWrongProblems(data.wrong_problems);
        });
}

function formatTags(tags) {
    return tags
        .split(',')
        .filter((tag) => !tag.startsWith('科目:') && !tag.startsWith('年级:') && !tag.startsWith('项目:'))
        .map((tag) => `<span class="tag">${tag}</span>`)
        .join('');
}

function displayWrongProblems(problems) {
    const container = document.getElementById('wrong-problems-list');
    const emptyMessage = document.getElementById('empty-message');

    if (!problems.length) {
        container.innerHTML = '';
        emptyMessage.classList.remove('hidden');
        return;
    }

    emptyMessage.classList.add('hidden');
    container.innerHTML = '';

    problems.forEach((problem) => {
        const card = document.createElement('div');
        card.className = 'wrong-problem-card';
        const questionClass = isWordProblem(problem) ? 'wrong-problem-question word-problem-inline' : 'wrong-problem-question';
        card.innerHTML = `
            <div class="wrong-problem-header">
                <div class="${questionClass}">${problem.question}</div>
                <div class="wrong-problem-stats">
                    <span class="stat-badge wrong">错误 ${problem.wrong_count} 次</span>
                    <span class="stat-badge correct">连对 ${problem.correct_streak}/3</span>
                </div>
            </div>
            <div class="wrong-problem-info">
                <p><strong>答案：</strong>${problem.answer_display}</p>
                <div class="wrong-problem-tags">
                    ${formatTags(problem.tags)}
                </div>
            </div>
            <div class="wrong-problem-actions">
                <button onclick="practiceSimilar(${problem.id}, '${problem.tags.replace(/'/g, "\\'")}')" class="btn">
                    练习相似题目
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}

function renderModalAnswerInputs(answerMode) {
    const container = document.querySelector('#modal-practice-section .answer-input');
    if (answerMode === 'quotient_remainder') {
        container.innerHTML = `
            <input type="number" id="modal-answer-quotient" placeholder="请输入商">
            <input type="number" id="modal-answer-remainder" placeholder="请输入余数">
            <button onclick="submitModalAnswer()" class="btn">提交</button>
        `;
    } else {
        container.innerHTML = `
            <input type="number" id="modal-answer" placeholder="请输入答案">
            <button onclick="submitModalAnswer()" class="btn">提交</button>
        `;
    }
}

function attachModalInputHandlers(answerMode) {
    if (answerMode === 'quotient_remainder') {
        const quotientInput = document.getElementById('modal-answer-quotient');
        const remainderInput = document.getElementById('modal-answer-remainder');

        quotientInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                remainderInput.focus();
            }
        });

        remainderInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                submitModalAnswer();
            }
        });

        quotientInput.focus();
        return;
    }

    const singleInput = document.getElementById('modal-answer');
    singleInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            submitModalAnswer();
        }
    });
    singleInput.focus();
}

function collectModalAnswer(answerMode) {
    if (answerMode === 'quotient_remainder') {
        const quotient = document.getElementById('modal-answer-quotient').value;
        const remainder = document.getElementById('modal-answer-remainder').value;
        if (quotient === '' || remainder === '') {
            alert('请输入商和余数');
            return null;
        }
        return parseInt(quotient, 10) * 100 + parseInt(remainder, 10);
    }

    const answer = document.getElementById('modal-answer').value;
    if (answer === '') {
        alert('请输入答案');
        return null;
    }
    return parseInt(answer, 10);
}

function persistModalAnswerRecord(problemId, userAnswer) {
    fetch('/api/submit_answer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            problem_id: problemId,
            user_answer: userAnswer
        })
    })
        .then((res) => res.json())
        .then((data) => {
            if (!data.success) {
                throw new Error(data.message || '提交答案失败');
            }
        })
        .catch((error) => {
            console.error('Failed to persist modal answer record:', error);
        });
}

function practiceSimilar(problemId, tags) {
    fetch('/api/get_similar_problems', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            tags,
            count: 5,
            exclude_id: problemId
        })
    })
        .then((res) => res.json())
        .then((data) => {
            if (!data.success) {
                alert(data.message || '获取相似题失败');
                return;
            }

            if (!data.problems.length) {
                alert('当前项目下没有找到足够相似的题目。');
                return;
            }

            modalProblems = data.problems;
            modalCurrentIndex = 0;
            modalCorrectCount = 0;
            modalWrongCount = 0;

            document.getElementById('modal-practice-section').classList.remove('hidden');
            document.getElementById('modal-result-section').classList.add('hidden');
            document.getElementById('practice-modal').classList.remove('hidden');
            document.getElementById('modal-total-count').textContent = modalProblems.length;

            showModalProblem();
        });
}

function showModalProblem() {
    if (modalCurrentIndex >= modalProblems.length) {
        showModalResults();
        return;
    }

    const problem = modalProblems[modalCurrentIndex];
    document.getElementById('modal-question').textContent = problem.question;
    updateModalProblemPresentation(problem);
    renderModalAnswerInputs(problem.answer_mode);
    attachModalInputHandlers(problem.answer_mode);
    document.getElementById('modal-feedback').classList.add('hidden');

    document.getElementById('modal-current-index').textContent = modalCurrentIndex + 1;
    document.getElementById('modal-correct-count').textContent = modalCorrectCount;
    document.getElementById('modal-wrong-count').textContent = modalWrongCount;

    updateModalProgress();
}

function submitModalAnswer() {
    if (isSubmittingModalAnswer) {
        return;
    }

    const problem = modalProblems[modalCurrentIndex];
    const userAnswer = collectModalAnswer(problem.answer_mode);
    if (userAnswer === null) {
        return;
    }

    isSubmittingModalAnswer = true;
    const isCorrect = userAnswer === problem.answer;
    const feedback = document.getElementById('modal-feedback');
    feedback.classList.remove('hidden');

    if (isCorrect) {
        feedback.textContent = '回答正确';
        feedback.className = 'feedback correct';
        modalCorrectCount++;
    } else {
        feedback.textContent = `回答错误，正确答案是：${problem.answer_display}`;
        feedback.className = 'feedback wrong';
        modalWrongCount++;
    }

    persistModalAnswerRecord(problem.id, userAnswer);

    setTimeout(() => {
        modalCurrentIndex++;
        isSubmittingModalAnswer = false;
        showModalProblem();
    }, 1000);
}

function updateModalProgress() {
    const progress = (modalCurrentIndex / modalProblems.length) * 100;
    document.getElementById('modal-progress-fill').style.width = `${progress}%`;
}

function showModalResults() {
    document.getElementById('modal-practice-section').classList.add('hidden');
    document.getElementById('modal-result-section').classList.remove('hidden');

    document.getElementById('modal-result-correct').textContent = modalCorrectCount;
    document.getElementById('modal-result-wrong').textContent = modalWrongCount;

    setTimeout(() => {
        loadWrongProblems();
    }, 500);
}

function closeModal() {
    document.getElementById('practice-modal').classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', function() {
    loadSessionBanner();
    loadWrongProblems();
});
