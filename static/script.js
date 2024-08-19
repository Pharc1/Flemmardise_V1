document.addEventListener('DOMContentLoaded', (event) => {
    const video = document.getElementById('video');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const status = document.getElementById('status');
    const sessionModal = document.getElementById('session-modal');
    const sessionForm = document.getElementById('session-form');

    let isRecording = false;
    let sessionDetails = {};

    startBtn.addEventListener('click', () => {
        sessionModal.style.display = 'block';
    });

    sessionForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sessionDetails = {
            activity: document.getElementById('activity').value,
            duration: document.getElementById('duration').value,
            motivation: document.getElementById('motivation').value,
            consequences: document.getElementById('consequences').value
        };
        sessionModal.style.display = 'none';
        startSession();
    });

    function startSession() {
        if (!isRecording) {
            fetch('/motivate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sessionDetails)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Session details saved:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });

            video.src = videoFeedUrl;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            status.textContent = 'Statut : En cours';
            status.classList.remove('status-off');
            status.classList.add('status-on');
            isRecording = true;
        }
    }

    stopBtn.addEventListener('click', () => {
        if (isRecording) {
            video.src = "";
            startBtn.disabled = false;
            stopBtn.disabled = true;
            status.textContent = 'Statut : Arrêté';
            status.classList.remove('status-on');
            status.classList.add('status-off');
            isRecording = false;
        }
    });

    function playMotivationalMessage() {
        const audio = new Audio('/static/speech.mp3');
        audio.play();
    }

    // Optionnel : Répéter pour vérifier si un nouveau fichier audio a été généré
    setInterval(() => {
        fetch('/check_motivation')
            .then(response => response.json())
            .then(data => {
                if (data.new_audio) {
                    playMotivationalMessage();
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }, 5000); // Vérifier toutes les 5 secondes
});
