document.addEventListener('DOMContentLoaded', (event) => {
    const video = document.getElementById('video');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const status = document.getElementById('status');

    let isRecording = false;

    startBtn.addEventListener('click', () => {
        if (!isRecording) {
            video.src = videoFeedUrl;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            status.textContent = 'Statut : En cours';
            status.classList.remove('status-off');
            status.classList.add('status-on');
            isRecording = true;
        }
    });

    stopBtn.addEventListener('click', () => {
        if (isRecording) {
            video.src = ""; // Clear the src to stop the video
            startBtn.disabled = false;
            stopBtn.disabled = true;
            status.textContent = 'Statut : Arrêté';
            status.classList.remove('status-on');
            status.classList.add('status-off');
            isRecording = false;
        }
    });
});