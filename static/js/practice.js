let problems = [];
let currentIndex = 0;
let correctCount = 0;
let wrongCount = 0;

function updateTagOptions() {
    const type = document.getElementById('problem-type').value;
    const additionTags = document.getElementById('addition-tags');
    const subtractionTags = document.getElementById('subtraction-tags');

    if (type === '加法') {
        additionTags.style.display = 'block';
        subtractionTags.style.display = 'none';
    } else if (type === '减法') {
        additionTags.style.display = 'none';
        subtractionTags.style.display = 'block';
    } else {
        additionTags.style.display = 'block';
        subtractionTags.style.display = 'block';
    }
}

function getSelectedTags() {
    const tags = [];
    const checkboxes = document.querySelectorAll('.tag-group input[type="checkbox"]:checked');
    checkboxes.forEach(cb => {
        tags.push(cb.value);
    });
    return tags;
}

function startPractice() {
    const count = document.getElementById('problem-count').value;
    const type = document.getElementById('problem-type').value;
    const tags = getSelectedTags();

    let url = `/api/get_problems?count=${count}`;
    if (type) {
        url += `&type=${encodeURIComponent(type)}`;
    }
    tags.forEach(tag => {
        url += `&tags[]=${encodeURIComponent(tag)}`;
    });

    fetch(url)
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            if (data.problems.length === 0) {
                alert('没有找到符合条件的题目，请调整筛选条件');
                return;
            }
            problems = data.problems;
            currentIndex = 0;
            correctCount = 0;
            wrongCount = 0;

            document.getElementById('setup-section').classList.add('hidden');
            document.getElementById('practice-section').classList.remove('hidden');
            document.getElementById('total-count').textContent = problems.length;

            showProblem();
        }
    });
}

function showProblem() {
    if (currentIndex >= problems.length) {
        showResults();
        return;
    }

    const problem = problems[currentIndex];
    document.getElementById('question').textContent = problem.question;
    document.getElementById('answer').value = '';
    document.getElementById('answer').focus();
    document.getElementById('feedback').classList.add('hidden');

    document.getElementById('current-index').textContent = currentIndex + 1;
    document.getElementById('correct-count').textContent = correctCount;
    document.getElementById('wrong-count').textContent = wrongCount;

    updateProgress();
}

function submitAnswer() {
    const answer = document.getElementById('answer').value;
    if (answer === '') {
        alert('请输入答案');
        return;
    }

    const problem = problems[currentIndex];

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
            const feedback = document.getElementById('feedback');
            feedback.classList.remove('hidden');

            if (data.is_correct) {
                feedback.textContent = '✓ 正确！';
                feedback.className = 'feedback correct';
                correctCount++;
            } else {
                feedback.textContent = `✗ 错误！正确答案是: ${data.correct_answer}`;
                feedback.className = 'feedback wrong';
                wrongCount++;
            }

            setTimeout(() => {
                currentIndex++;
                showProblem();
            }, 1500);
        }
    });
}

function updateProgress() {
    const progress = (currentIndex / problems.length) * 100;
    document.getElementById('progress-fill').style.width = progress + '%';
}

function showResults() {
    document.getElementById('practice-section').classList.add('hidden');
    document.getElementById('result-section').classList.remove('hidden');

    const total = correctCount + wrongCount;
    const accuracy = total > 0 ? (correctCount / total * 100).toFixed(1) : 0;

    document.getElementById('result-total').textContent = total;
    document.getElementById('result-correct').textContent = correctCount;
    document.getElementById('result-wrong').textContent = wrongCount;
    document.getElementById('result-accuracy').textContent = accuracy + '%';
}

// 回车提交答案
document.addEventListener('DOMContentLoaded', function() {
    const answerInput = document.getElementById('answer');
    if (answerInput) {
        answerInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                submitAnswer();
            }
        });
    }

    // 初始化标签显示
    updateTagOptions();
});
