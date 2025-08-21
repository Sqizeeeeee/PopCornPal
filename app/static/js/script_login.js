document.addEventListener("DOMContentLoaded", () => {
    const flashes = document.querySelectorAll(".flash-messages li");
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.classList.add("hide");
            setTimeout(() => flash.remove(), 500);
        }, 3000);
    });
    const emojis = ["🎫", "🎰", "💰", "🏃‍♂️", "🎥", "🎬", "🍿", "🎞️", "🏴‍☠️", "🇺🇸", "👮‍♂️", "🚔", "🕵️‍♂️", "🚨", "💼", " 🚀", "✈️", "🍕", "☢️", "⁉️", "👑", "🗡️", "🎫", "🎰", "💰", "🏃‍♂️", "🎥", "🎬", "🍿", "🎞️", "🏴‍☠️", "🇺🇸", "👮‍♂️", "🚔", "🕵️‍♂️", "🚨", "💼", " 🚀", "✈️", "🍕", "☢️", "⁉️", "👑", "🗡️", "⭐️", "❄️", "🌊", "💧", "⚽️", "🌄", "🌃", "🔥", "🐬", "⭐️", "❄️", "🌊", "💧", "⚽️", "🌄", "🌃", "🔥", "🐬"];
    const body = document.body;

    emojis.forEach(emoji => {
        const div = document.createElement("div");
        div.classList.add("emoji-bg");
        div.textContent = emoji;
        div.style.left = Math.random() * 95 + "%";
        div.style.fontSize = (20 + Math.random() * 30) + "px";
        div.style.animationDuration = (6 + Math.random() * 6) + "s";
        body.appendChild(div);
    });
});