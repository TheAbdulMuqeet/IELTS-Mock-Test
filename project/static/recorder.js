document.addEventListener("DOMContentLoaded", () => {
    document.getElementById('startButton').addEventListener('click', async () => {

        try {
            const response = await fetch('/record/', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            const notification = document.getElementById("notification");
            const notificationMessage = document.getElementById("notification-message");

            if (data.status === "ok") {
                notificationMessage.innerHTML = data.message;
                const textarea = document.getElementById("textarea");
                textarea.value = data.output;
            } else {
                notificationMessage.innerHTML = "Error: " + data.message;
            }

            notification.style.filter = "opacity(1)";
            notification.style.display = "flex";

        } catch (error) {
            console.error("Error:", error);
        }

        audioChunks = [];
    });

    document.getElementById('startButton').disabled = true;
    document.getElementById('stopButton').disabled = false;
});

document.getElementById('stopButton').addEventListener('click', () => {
    mediaRecorder.stop();

    document.getElementById('startButton').disabled = false;
    document.getElementById('stopButton').disabled = true;
});