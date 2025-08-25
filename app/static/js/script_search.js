document.addEventListener('DOMContentLoaded', () => {
    // Находим все кастомные чекбоксы
    const checkboxes = document.querySelectorAll('.custom-checkbox');

    checkboxes.forEach(label => {
        const input = label.querySelector('input[type="checkbox"]');
        const ui = label.querySelector('.checkbox-ui');
        const text = label.querySelector('.checkbox-text');

        if (!input || !ui || !text) return;

        // При клике на лейбл (checkbox), меняем визуал
        input.addEventListener('change', () => {
            if (input.checked) {
                ui.style.backgroundColor = 'rgba(255, 107, 107, 0.1)';
                text.style.color = '#ff6b6b';
                text.style.fontWeight = '600';
            } else {
                ui.style.backgroundColor = '';
                text.style.color = '#fff';
                text.style.fontWeight = '400';
            }
        });

        // Инициализация визуала при загрузке (если уже checked)
        if (input.checked) {
            ui.style.backgroundColor = 'rgba(255, 107, 107, 0.1)';
            text.style.color = '#ff6b6b';
            text.style.fontWeight = '600';
        }
    });
});