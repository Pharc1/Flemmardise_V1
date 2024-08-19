document.addEventListener('DOMContentLoaded', (event) => {
    const video = document.getElementById('video');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const status = document.getElementById('status');

    let stream = null;

    // Fonction pour démarrer l'enregistrement
    startBtn.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.play();
            startBtn.disabled = true;
            stopBtn.disabled = false;
            status.textContent = 'Statut : En cours';
            status.classList.remove('status-off');
            status.classList.add('status-on');
        } catch (error) {
            console.error('Erreur lors de l\'accès à la caméra:', error);
        }
    });

    // Fonction pour arrêter l'enregistrement
    stopBtn.addEventListener('click', () => {
        if (stream) {
            let tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
            video.srcObject = null;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            status.textContent = 'Statut : Arrêté';
            status.classList.remove('status-on');
            status.classList.add('status-off');
        }
    });
});
