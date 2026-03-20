let problems = [];
let currentIndex = 0;
let correctCount = 0;
let wrongCount = 0;
let activeProjectConfig = null;
let currentPracticeSelection = null;
let savedPracticeSettings = null;
let lastPersistedPracticeSettingsJson = null;

function setSavedPracticeSettings(settings) {
    savedPracticeSettings = settings || null;
    lastPersistedPracticeSettingsJson = settings ? JSON.stringify(settings) : null;
}

function getCurrentPracticeSettingsPayload() {
    const countInput = document.getElementById('problem-count');
    const typeSelect = document.getElementById('problem-type');
    if (!countInput || !typeSelect) {
        return null;
    }

    const min = parseInt(countInput.min || '1', 10);
    const max = parseInt(countInput.max || '50', 10);
    const parsedCount = parseInt(countInput.value, 10);
    const count = Number.isNaN(parsedCount) ? 10 : Math.min(Math.max(parsedCount, min), max);

    return {
        count,
        type: typeSelect.value,
        tags: getSelectedTags()
    };
}

function saveCurrentPracticeSettings() {
    if (!currentPracticeSelection) {
        return;
    }

    const settings = getCurrentPracticeSettingsPayload();
    if (!settings) {
        return;
    }

    const settingsJson = JSON.stringify(settings);
    if (settingsJson === lastPersistedPracticeSettingsJson) {
        return;
    }

    fetch('/api/save_practice_settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: settingsJson
    })
        .then((res) => res.json())
        .then((data) => {
            if (!data.success) {
                throw new Error(data.message || '淇濆瓨缁冧範璁剧疆澶辫触');
            }
            setSavedPracticeSettings(data.practice_settings || settings);
        })
        .catch((error) => {
            console.error('Failed to save practice settings:', error);
        });
}

function restorePracticeSettings() {
    const countInput = document.getElementById('problem-count');
    const typeSelect = document.getElementById('problem-type');
    const tagCheckboxes = document.querySelectorAll('.tag-group input[type="checkbox"]');
    const savedSettings = savedPracticeSettings;

    if (savedSettings && countInput) {
        const min = parseInt(countInput.min || '1', 10);
        const max = parseInt(countInput.max || '50', 10);
        const savedCount = parseInt(savedSettings.count, 10);
        if (!Number.isNaN(savedCount) && savedCount >= min && savedCount <= max) {
            countInput.value = savedCount;
        }
    }

    if (savedSettings && typeSelect) {
        const availableValues = Array.from(typeSelect.options).map((option) => option.value);
        if (availableValues.includes(savedSettings.type)) {
            typeSelect.value = savedSettings.type;
        }
    }

    const savedTags = new Set((savedSettings && savedSettings.tags) || []);
    tagCheckboxes.forEach((checkbox) => {
        checkbox.checked = savedTags.has(checkbox.value);
    });

    updateTagOptions();
}

function attachPracticeSettingsListeners() {
    const countInput = document.getElementById('problem-count');
    const typeSelect = document.getElementById('problem-type');
    const tagCheckboxes = document.querySelectorAll('.tag-group input[type="checkbox"]');

    if (countInput) {
        countInput.addEventListener('change', saveCurrentPracticeSettings);
    }

    if (typeSelect) {
        typeSelect.addEventListener('change', saveCurrentPracticeSettings);
    }

    tagCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', saveCurrentPracticeSettings);
    });
}

function getSelectedTags() {
    const tags = [];
    const checkboxes = document.querySelectorAll('.tag-group input[type="checkbox"]:checked');
    checkboxes.forEach((checkbox) => {
        tags.push(checkbox.value);
    });
    return tags;
}

function renderTypeOptions(typeOptions) {
    const select = document.getElementById('problem-type');
    select.innerHTML = '';

    typeOptions.forEach((optionConfig) => {
        const option = document.createElement('option');
        option.value = optionConfig.value;
        option.textContent = optionConfig.label;
        select.appendChild(option);
    });
}

function renderTagGroups(tagGroups) {
    const container = document.getElementById('tag-groups-container');
    container.innerHTML = '';

    tagGroups.forEach((group) => {
        const groupElement = document.createElement('div');
        groupElement.className = 'tag-group';
        groupElement.dataset.visibleFor = JSON.stringify(group.visible_for || ['']);

        const title = document.createElement('h3');
        title.textContent = group.title;
        groupElement.appendChild(title);

        const grid = document.createElement('div');
        grid.className = 'checkbox-grid';

        group.options.forEach((tagValue) => {
            const label = document.createElement('label');
            label.innerHTML = `<input type="checkbox" value="${tagValue}"> ${tagValue}`;
            grid.appendChild(label);
        });

        groupElement.appendChild(grid);
        container.appendChild(groupElement);
    });
}

function updateTagOptions() {
    const selectedType = document.getElementById('problem-type').value;
    const groups = document.querySelectorAll('.tag-group');

    groups.forEach((group) => {
        const visibleFor = JSON.parse(group.dataset.visibleFor || '[""]');
        group.style.display = visibleFor.includes(selectedType) ? 'block' : 'none';
    });
}

function renderAnswerInputs(answerMode) {
    const container = document.getElementById('answer-input-container');

    if (answerMode === 'quotient_remainder') {
        container.innerHTML = `
            <input type="number" id="answer-quotient" placeholder="请输入商">
            <input type="number" id="answer-remainder" placeholder="请输入余数">
            <button onclick="submitAnswer()" class="btn">提交</button>
        `;
        return;
    }

    container.innerHTML = `
        <input type="number" id="answer" placeholder="请输入答案">
        <button onclick="submitAnswer()" class="btn">提交</button>
    `;
}

function focusAnswerInput(answerMode) {
    if (answerMode === 'quotient_remainder') {
        document.getElementById('answer-quotient').focus();
    } else {
        document.getElementById('answer').focus();
    }
}

function collectAnswer(answerMode) {
    if (answerMode === 'quotient_remainder') {
        const quotient = document.getElementById('answer-quotient').value;
        const remainder = document.getElementById('answer-remainder').value;
        if (quotient === '' || remainder === '') {
            alert('请输入商和余数');
            return null;
        }
        return {
            user_answer: parseInt(quotient, 10) * 100 + parseInt(remainder, 10)
        };
    }

    const answer = document.getElementById('answer').value;
    if (answer === '') {
        alert('请输入答案');
        return null;
    }

    return {
        user_answer: parseInt(answer, 10)
    };
}

function attachAnswerKeyHandlers() {
    const singleInput = document.getElementById('answer');
    if (singleInput) {
        singleInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                submitAnswer();
            }
        });
    }

    const quotientInput = document.getElementById('answer-quotient');
    if (quotientInput) {
        quotientInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                const remainderInput = document.getElementById('answer-remainder');
                if (remainderInput) {
                    remainderInput.focus();
                }
            }
        });
    }

    const remainderInput = document.getElementById('answer-remainder');
    if (remainderInput) {
        remainderInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                submitAnswer();
            }
        });
    }
}

function buildProblemsUrl() {
    const count = document.getElementById('problem-count').value;
    const type = document.getElementById('problem-type').value;
    const tags = getSelectedTags();

    let url = `/api/get_problems?count=${count}`;
    if (type) {
        url += `&type=${encodeURIComponent(type)}`;
    }
    tags.forEach((tag) => {
        url += `&tags[]=${encodeURIComponent(tag)}`;
    });
    return url;
}

function debugQuery() {
    const type = document.getElementById('problem-type').value;
    const tags = getSelectedTags();

    let url = '/api/debug_problems?';
    if (type) {
        url += `type=${encodeURIComponent(type)}&`;
    }
    tags.forEach((tag) => {
        url += `tags[]=${encodeURIComponent(tag)}&`;
    });

    fetch(url)
        .then((res) => res.json())
        .then((data) => {
            if (!data.success) {
                alert(data.message || '调试查询失败');
                return;
            }

            document.getElementById('debug-section').classList.remove('hidden');
            document.getElementById('debug-sql').textContent = data.sql;
            document.getElementById('debug-total').textContent = data.total;

            const tbody = document.getElementById('debug-table-body');
            tbody.innerHTML = '';
            data.problems.forEach((problem) => {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #eee';
                tr.innerHTML = `
                    <td style="padding: 6px 8px;">${problem.id}</td>
                    <td style="padding: 6px 8px;">${problem.question}</td>
                    <td style="padding: 6px 8px;">${problem.answer_display}</td>
                    <td style="padding: 6px 8px;">${problem.type}</td>
                    <td style="padding: 6px 8px; font-size: 12px; color: #666;">${problem.tags}</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function startPractice() {
    saveCurrentPracticeSettings();

    fetch(buildProblemsUrl())
        .then((res) => res.json())
        .then((data) => {
            if (!data.success) {
                alert(data.message || '获取题目失败');
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
        });
}

function exportPdf() {
    fetch(buildProblemsUrl())
        .then((res) => res.json())
        .then((data) => {
            if (!data.success) {
                alert(data.message || '获取题目失败');
                return;
            }

            const printWindow = window.open('', '_blank');
            if (!printWindow) {
                alert('请允许弹出窗口后再导出 PDF');
                return;
            }

            let html = `
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <title>数学练习单</title>
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif, 'KaiTi';
                        margin: 0;
                        padding: 20px;
                        color: #000;
                    }
                    .header {
                        text-align: center;
                        margin-bottom: 30px;
                    }
                    .header h1 {
                        font-size: 24px;
                        margin: 0 0 10px 0;
                    }
                    .student-info {
                        display: flex;
                        justify-content: flex-end;
                        gap: 20px;
                        font-size: 16px;
                        margin-bottom: 20px;
                    }
                    .student-info span {
                        min-width: 120px;
                    }
                    .grid {
                        display: grid;
                        grid-template-columns: repeat(5, 1fr);
                        gap: 30px 40px;
                        width: 100%;
                    }
                    .problem {
                        font-size: 18px;
                        padding: 10px 5px;
                        white-space: nowrap;
                    }
                    @media print {
                        @page {
                            margin: 1.5cm;
                            size: A4 portrait;
                        }
                        body {
                            padding: 0;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>数学练习单</h1>
                </div>
                <div class="student-info">
                    <span>姓名：________</span>
                    <span>班级：________</span>
                    <span>得分：________</span>
                </div>
                <div class="grid">
            `;

            data.problems.forEach((problem) => {
                const printableQuestion = problem.question.replace(/\?/g, '___');
                html += `
                    <div class="problem">
                        ${printableQuestion}
                    </div>
                `;
            });

            html += `
                </div>
                <script>
                    window.onload = function() {
                        setTimeout(() => {
                            window.print();
                        }, 500);
                    };
                </script>
            </body>
            </html>
            `;

            printWindow.document.open();
            printWindow.document.write(html);
            printWindow.document.close();
        });
}

function showProblem() {
    if (currentIndex >= problems.length) {
        showResults();
        return;
    }

    const problem = problems[currentIndex];
    document.getElementById('question').textContent = problem.question;
    renderAnswerInputs(problem.answer_mode);
    attachAnswerKeyHandlers();
    focusAnswerInput(problem.answer_mode);
    document.getElementById('feedback').classList.add('hidden');

    document.getElementById('current-index').textContent = currentIndex + 1;
    document.getElementById('correct-count').textContent = correctCount;
    document.getElementById('wrong-count').textContent = wrongCount;

    updateProgress();
}

function submitAnswer() {
    const problem = problems[currentIndex];
    const payload = collectAnswer(problem.answer_mode);
    if (!payload) {
        return;
    }

    fetch('/api/submit_answer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            problem_id: problem.id,
            ...payload
        })
    })
        .then((res) => res.json())
        .then((data) => {
            if (!data.success) {
                alert(data.message || '提交答案失败');
                return;
            }

            const feedback = document.getElementById('feedback');
            feedback.classList.remove('hidden');

            if (data.is_correct) {
                feedback.textContent = '回答正确';
                feedback.className = 'feedback correct';
                correctCount++;
            } else {
                feedback.textContent = `回答错误，正确答案是：${data.correct_answer_display}`;
                feedback.className = 'feedback wrong';
                wrongCount++;
            }

            setTimeout(() => {
                currentIndex++;
                showProblem();
            }, 1500);
        });
}

function updateProgress() {
    const progress = (currentIndex / problems.length) * 100;
    document.getElementById('progress-fill').style.width = `${progress}%`;
}

function showResults() {
    document.getElementById('practice-section').classList.add('hidden');
    document.getElementById('result-section').classList.remove('hidden');

    const total = correctCount + wrongCount;
    const accuracy = total > 0 ? (correctCount / total * 100).toFixed(1) : 0;

    document.getElementById('result-total').textContent = total;
    document.getElementById('result-correct').textContent = correctCount;
    document.getElementById('result-wrong').textContent = wrongCount;
    document.getElementById('result-accuracy').textContent = `${accuracy}%`;
}

function initializePracticePage() {
    fetch('/api/session_state')
        .then((res) => res.json())
        .then((data) => {
            if (!data.success || !data.logged_in) {
                location.href = '/';
                return;
            }

            const selection = data.selection || {};
            const catalog = data.catalog || [];
            const projectEntry = catalog.find((item) => (
                item.subject === selection.subject &&
                item.grade === selection.grade &&
                item.project === selection.project
            ));

            if (!projectEntry) {
                alert('当前项目配置不存在');
                location.href = '/';
                return;
            }

            activeProjectConfig = projectEntry.practice_config;
            currentPracticeSelection = selection;
            setSavedPracticeSettings(data.practice_settings);

            document.getElementById('banner-subject').textContent = selection.subject || '未选择';
            document.getElementById('banner-grade').textContent = selection.grade || '未选择';
            document.getElementById('banner-project').textContent = selection.project || '未选择';

            renderTypeOptions(activeProjectConfig.type_options || [{value: '', label: '全部'}]);
            renderTagGroups(activeProjectConfig.tag_groups || []);
            restorePracticeSettings();
            attachPracticeSettingsListeners();
        });
}

document.addEventListener('DOMContentLoaded', function() {
    initializePracticePage();
});
