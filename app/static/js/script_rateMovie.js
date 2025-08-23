// script_rateMovie.js

document.addEventListener('DOMContentLoaded', () => {
    // Находим все элементы слайдера
    document.querySelectorAll('.rating-control').forEach(control => {
        const slider = control.querySelector('.slider');
        const valueDisplay = control.querySelector('.slider-value');

        // Сразу устанавливаем значение при загрузке страницы
        valueDisplay.textContent = slider.value;

        // Обновляем значение при изменении ползунка
        slider.addEventListener('input', () => {
            valueDisplay.textContent = slider.value;
        });
    });
});