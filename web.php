<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Classroom by Dux</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 10px 20px;
            background-color: ; /* Dark red */
            color: #822433;
        }
        .header img {
            height: 50px;
            margin-right: 20px;
        }
        .header h1 {
            margin: 0 auto;
            font-size: 24px;
        }
        .container {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            padding: 20px;
        }
        .component-box {
            background-color: #822433; 
            color: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            flex: 1 1 calc(33% - 40px);
            box-sizing: border-box;
        }
        .component-box h2 {
            margin-top: 0;
        }
        .switch {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .switch input {
            display: none;
        }
        .switch label {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }
        .switch label input:checked + .slider:before {
            transform: translateX(26px);
        }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        .switch input:checked + .slider {
            background-color: #2196F3;
        }
        .button {
            margin-top: 10px;
            display: none;
            padding: 10px 20px;
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .button:hover {
            background-color: #1e7eaa;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="assets/RCAIoT_logo.png" alt="Company Logo">
        <h1>Smart Classroom by Dux</h1>
    </div>
    <div class="container">
        <div class="component-box">
            <h2>Lamp</h2>
            <div class="switch">
                <label>
                    <input type="checkbox" onchange="controlDevice('lamp', this.checked ? 'on' : 'off')">
                    <span class="slider"></span>
                </label>
            </div>
        </div>
        <div class="component-box">
            <h2>Projector</h2>
            <div class="switch">
                <label>
                    <input type="checkbox" onchange="controlDevice('projector', this.checked ? 'on' : 'off', this)">
                    <span class="slider"></span>
                </label>
            </div>
            <button id="startSharingButton" class="button" onclick="startScreenSharing()">Start Sharing</button>
        </div>
        <div class="component-box">
            <h2>AC</h2>
            <div class="switch">
                <label>
                    <input type="checkbox" onchange="controlDevice('ac', this.checked ? 'on' : 'off')">
                    <span class="slider"></span>
                </label>
            </div>
        </div>
        <div class="component-box">
            <h2>Temperature</h2>
            <div id="temperatureDisplay">Loading...</div>
        </div>
    </div>

    <script>
       function controlDevice(device, action, element) {
    if (window.fetch) {
        fetch('http://10.102.248.25:5000/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                'device': device,
                'action': action
            })
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
                    document.getElementById('startSharingButton').style.display = 'block';
                } else if (device === 'projector' && action === 'off') {
                    document.getElementById('startSharingButton').style.display = 'none';
                }
            } else {
                alert('Error controlling the ' + device);
                if (element) {
                    element.checked = !element.checked;  // revert the switch state if there's an error
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error controlling the ' + device);
            if (element) {
                element.checked = !element.checked;  // revert the switch state if there's an error
            }
        });
    } else {
        // Fallback for browsers that do not support fetch
        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'http://10.102.248.25:5000/control', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    if (data.status === 'success') {
                        alert(device.charAt(0).toUpperCase() + device.slice(1) + ' ' + action);
                        if (device === 'projector' && action === 'on') {
                            document.getElementById('startSharingButton').style.display = 'block';
                        } else if (device === 'projector' && action === 'off') {
                            document.getElementById('startSharingButton').style.display = 'none';
                        }
                    } else {
                        alert('Error controlling the ' + device);
                        if (element) {
                            element.checked = !element.checked;  // revert the switch state if there's an error
                        }
                    }
                } else {
                    alert('Error controlling the ' + device);
                    if (element) {
                        element.checked = !element.checked;  // revert the switch state if there's an error
                    }
                }
            }
        };
        xhr.send('device=' + device + '&action=' + action);
    }
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

        function updateTemperature() {
            fetch('http://10.102.248.25:5000/temperature')
            .then(response => response.json())
            .then(data => {
                document.getElementById('temperatureDisplay').textContent = data.temperature + '°C';
            })
            .catch(error => {
                console.error('Error fetching temperature:', error);
                document.getElementById('temperatureDisplay').textContent = 'Error loading temperature';
            });
        }

        // Initial temperature load and periodic updates
        updateTemperature();
        setInterval(updateTemperature, 60000); // Update every minute
    </script>
</body>
</html>
