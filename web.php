<!DOCTYPE html>
<html>
<head>
    <title>Lamp and Projector Control</title>
</head>
<body>
    <h1>Control the Lamp and Projector</h1>
    <button onclick="controlDevice('lamp', 'on')">Turn On Lamp</button>
    <button onclick="controlDevice('lamp', 'off')">Turn Off Lamp</button>
    <button onclick="controlDevice('projector', 'on')">Turn On Projector</button>
    <button onclick="controlDevice('projector', 'off')">Turn Off Projector</button>

    <script>
        function controlDevice(device, action) {
            fetch('http://10.102.248.25:5000/control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: 'device=' + device + '&action=' + action
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    alert(device.charAt(0).toUpperCase() + device.slice(1) + ' ' + action);
                    if (device === 'projector' && action === 'on') {
                        startScreenSharing();
                    }
                } else {
                    alert('Error controlling the ' + device);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error controlling the ' + device);
            });
        }

        function startScreenSharing() {
            navigator.mediaDevices.getDisplayMedia({ video: true })
            .then(stream => {
                const videoTrack = stream.getVideoTracks()[0];
                const video = document.createElement('video');
                video.srcObject = new MediaStream([videoTrack]);
                video.play();

                const peerConnection = new RTCPeerConnection();
                peerConnection.addTrack(videoTrack, stream);

                // Replace 'YOUR_SIGNALING_SERVER_URL' with your signaling server URL
                const signaling = new WebSocket('ws://YOUR_SIGNALING_SERVER_URL');
                signaling.onmessage = event => {
                    const signal = JSON.parse(event.data);
                    if (signal.type === 'offer') {
                        peerConnection.setRemoteDescription(signal);
                        peerConnection.createAnswer()
                        .then(answer => {
                            peerConnection.setLocalDescription(answer);
                            signaling.send(JSON.stringify(answer));
                        });
                    } else if (signal.type === 'answer') {
                        peerConnection.setRemoteDescription(signal);
                    }
                };
            })
            .catch(error => {
                console.error('Error starting screen sharing:', error);
                alert('Error starting screen sharing');
            });
        }
    </script>
</body>
</html>
