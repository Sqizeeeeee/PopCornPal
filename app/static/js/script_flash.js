document.addEventListener('DOMContentLoaded', () => {
    const surveyData = {};
    const form = document.querySelector('.survey-form');
    if (!form) return;

    function updateSliderColor(slider) {
        const percent = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
        slider.style.background = `linear-gradient(to right, #ff6b6b 0%, #ff6b6b ${percent}%, #555 ${percent}%, #555 100%)`;
    }

    document.querySelectorAll('.survey-item').forEach(item => {
        const slider = item.querySelector('.slider');
        const output = item.querySelector('.slider-value');
        const skip = item.querySelector('.skip-label input[type="checkbox"]');
        const movieId = item.dataset.id;

        if (!slider || !output || !skip) return;

        let val = parseFloat(slider.value);
        surveyData[movieId] = val;
        output.textContent = val.toFixed(1);
        updateSliderColor(slider);

        const updateValue = () => {
            if (!skip.checked) {
                val = parseFloat(slider.value);
                surveyData[movieId] = val;
                output.textContent = val.toFixed(1);
                updateSliderColor(slider);
            }
        };

        slider.addEventListener('input', updateValue);
        slider.addEventListener('change', updateValue);

        skip.addEventListener('change', () => {
            if (skip.checked) {
                delete surveyData[movieId];
                slider.disabled = true;
                output.textContent = '—';
                slider.style.background = '#555';
            } else {
                slider.disabled = false;
                val = parseFloat(slider.value);
                surveyData[movieId] = val;
                output.textContent = val.toFixed(1);
                updateSliderColor(slider);
            }
        });
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        if (Object.keys(surveyData).length === 0) {
            addFlash('Please rate at least one movie or skip some.', 'error');
            return;
        }

        fetch('/survey', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(surveyData)
        })
        .then(res => res.json())
        .then(data => {
            addFlash(data.message, 'success');
            setTimeout(() => {
                window.location.href = '/profile';
            }, 1500);
        })
        .catch(err => {
            addFlash('Error sending data', 'error');
            console.error(err);
        });
    });

    // ⚡ Добавление нового flash-сообщения
    function addFlash(message, category = 'info') {
        const container = document.querySelector('.flash-container') || createFlashContainer();
        const flash = document.createElement('div');
        flash.className = `flash-message ${category}`;
        flash.innerHTML = `
            <span>${message}</span>
            <button class="flash-close">&times;</button>
        `;
        container.appendChild(flash);

        // 👉 тут НЕ трогаем fade-out и таймер
        // этим займётся script_flash.js
    }

    function createFlashContainer() {
        const container = document.createElement('div');
        container.className = 'flash-container';
        document.body.prepend(container);
        return container;
    }
});