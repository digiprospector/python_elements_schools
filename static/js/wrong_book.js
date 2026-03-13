let modalProblems = [];
let modalCurrentIndex = 0;
let modalCorrectCount = 0;
let modalWrongCount = 0;
let currentWrongProblem = null;

// 加载错题本
function loadWrongProblems() {
    fetch('/api/get_wrong_problems')
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            displayWrongProblems(data.wrong_problems);
        } else {
            alert(data.message || '加载失败');
            if (data.message === '请先登录') {
                location.href = '/';
            }
        }
    });
}

// 显示错题列表
function displayWrongProblems(problems) {
    const container = document.getElementById('wrong-problems-list');
    const emptyMessage = document.getElementById('empty-message');

    if (problems.length === 0) {
        container.innerHTML = '';
        emptyMessage.classList.remove('hidden');
        return;
    }

    emptyMessage.classList.add('hidden');
    container.innerHTML = '';

    problems.forEach(problem => {
        const card = document.createElement('div');
        card.className = 'wrong-problem-card';

        const tags = problem.tags.split(',');
        const tagsHtml = tags.map(tag => `<span class="tag">${tag}</span>`).join('');

        card.innerHTML = `
            <div class="wrong-problem-header">
                <div class="wrong-problem-question">${problem.question}</div>
                <div class="wrong-problem-stats">
                    <span class="stat-badge wrong">错误 ${problem.wrong_count} 次</span>
                    <span class="stat-badge correct">连对 ${problem.correct_streak}/3</span>
                </div>
            </div>
            <div class="wrong-problem-info">
                <p><strong>答案:</strong> ${problem.answer}</p>
                <div class="wrong-problem-tags">
                    ${tagsHtml}
                </div>
            </div>
            <div class="wrong-problem-actions">
                <button onclick="practiceSimilar('${problem.tags}', ${problem.id})" class="btn">
                    练习相似题目
                </button>
            </div>
        `;

        container.appendChild(card);
    });
}

// 练习相似题目
function practiceSimilar(tags, problemId) {
    currentWrongProblem = { tags, problemId };

    fetch('/api/get_similar_problems', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            tags: tags,
            count: 5,
            exclude_id: problemId
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            if (data.problems.length === 0) {
                alert('没有找到相似的题目');
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
        }
    });
}

// 显示弹窗中的题目
function showModalProblem() {
    if (modalCurrentIndex >= modalProblems.length) {
        showModalResults();
        return;
    }

    const problem = modalProblems[modalCurrentIndex];
    document.getElementById('modal-question').textContent = problem.question;
    document.getElementById('modal-answer').value = '';
    document.getElementById('modal-answer').focus();
    document.getElementById('modal-feedback').classList.add('hidden');

    document.getElementById('modal-current-index').textContent = modalCurrentIndex + 1;
    document.getElementById('modal-correct-count').textContent = modalCorrectCount;
    document.getElementById('modal-wrong-count').textContent = modalWrongCount;

    updateModalProgress();
}

// 提交弹窗中的答案
function submitModalAnswer() {
    const answer = document.getElementById('modal-answer').value;
    if (answer === '') {
        alert('请输入答案');
        return;
    }

    const problem = modalProblems[modalCurrentIndex];

    fetch('/api/submit_answer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            problem_id: problem.id,
            user_answer: parseInt(answer)
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const feedback = document.getElementById('modal-feedback');
            feedback.classList.remove('hidden');

            if (data.is_correct) {
                feedback.textContent = '✓ 正确！';
                feedback.className = 'feedback correct';
                modalCorrectCount++;
            } else {
                feedback.textContent = `✗ 错误！正确答案是: ${data.correct_answer}`;
                feedback.className = 'feedback wrong';
                modalWrongCount++;
            }

            setTimeout(() => {
                modalCurrentIndex++;
                showModalProblem();
            }, 1500);
        }
    });
}

// 更新弹窗进度条
function updateModalProgress() {
    const progress = (modalCurrentIndex / modalProblems.length) * 100;
    document.getElementById('modal-progress-fill').style.width = progress + '%';
}

// 显示弹窗结果
function showModalResults() {
    document.getElementById('modal-practice-section').classList.add('hidden');
    document.getElementById('modal-result-section').classList.remove('hidden');

    document.getElementById('modal-result-correct').textContent = modalCorrectCount;
    document.getElementById('modal-result-wrong').textContent = modalWrongCount;

    // 重新加载错题本（可能有题目被移除了）
    setTimeout(() => {
        loadWrongProblems();
    }, 500);
}

// 关闭弹窗
function closeModal() {
    document.getElementById('practice-modal').classList.add('hidden');
}

// 回车提交答案
document.addEventListener('DOMContentLoaded', function() {
    loadWrongProblems();

    const modalAnswer = document.getElementById('modal-answer');
    if (modalAnswer) {
        modalAnswer.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                submitModalAnswer();
            }
        });
    }
});
