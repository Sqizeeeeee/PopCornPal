document.addEventListener('DOMContentLoaded', function () {
      const blocks = document.querySelectorAll('.genre-block');

      // подготовка: добавить класс fade-in и задержку через --stagger
      blocks.forEach((el, idx) => {
        el.style.setProperty('--stagger', (idx % 9) * 60 + 'ms'); 
        el.classList.add('fade-in');
      });

      // небольшой таймаут, чтобы браузер успел применить начальные стили
      setTimeout(() => {
        const obs = new IntersectionObserver((entries, observer) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('visible');
              observer.unobserve(entry.target); // анимация один раз
            }
          });
        }, { threshold: 0.15 });

        blocks.forEach(el => obs.observe(el));
      }, 50); // 50ms достаточно
    });