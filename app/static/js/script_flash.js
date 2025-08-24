document.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash-message');

    flashes.forEach(flash => {
        const progress = flash.querySelector('.flash-progress');
        const duration = 5000; // 5 секунд до закрытия

        if (progress) {
            progress.style.animationDuration = duration + "ms";
        }

        // Закрытие при клике
        flash.querySelector('.flash-close').addEventListener('click', () => {
            flash.classList.add('fade-out');
            setTimeout(() => flash.remove(), 500);
        });

        // Авто-скрытие
        setTimeout(() => {
            flash.classList.add('fade-out');
            setTimeout(() => flash.remove(), 500);
        }, duration);
    });
});