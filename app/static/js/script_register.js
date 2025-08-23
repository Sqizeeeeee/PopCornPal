document.addEventListener("DOMContentLoaded", () => {
    // Генерация анимированных эмодзи
    const emojis = ["🎫", "🎰", "💰", "🏃‍♂️", "🎥", "🎬", "🍿", "🎞️", "🏴‍☠️", "🇺🇸", "👮‍♂️", "🚔", "🕵️‍♂️", "🚨", "💼", "🚀", "✈️", "🍕", "☢️", "⁉️", "👑", "🗡️", "⭐️", "❄️", "🌊", "💧", "⚽️", "🌄", "🌃", "🔥", "🐬", "🎫", "🎰", "💰", "🏃‍♂️", "🎥", "🎬", "🍿", "🎞️", "🏴‍☠️", "🇺🇸", "👮‍♂️", "🚔", "🕵️‍♂️", "🚨", "💼", "🚀", "✈️", "🍕", "☢️", "⁉️", "👑", "🗡️", "⭐️", "❄️", "🌊", "💧", "⚽️", "🌄", "🌃", "🔥", "🐬"];
    const body = document.body;

    emojis.forEach(emoji => {
        const div = document.createElement("div");
        div.classList.add("emoji-bg");
        div.textContent = emoji;
        div.style.left = Math.random() * 95 + "%";
        div.style.fontSize = (20 + Math.random() * 30) + "px";
        div.style.animationDuration = (8 + Math.random() * 8) + "s";
        body.appendChild(div);
    });
});