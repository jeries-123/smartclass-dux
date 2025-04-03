document.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM fully loaded');

    let signalingSocket;
    let peerConnection;
    let screenStream;
    
    const client_id = Math.random().toString(36).substring(7);

    // Function to connect to the WebSocket server
    function connectWebSocket() {
        
        //laptop ip address , because it is communicating with the signaling server which is running on the laptop
        signalingSocket = new WebSocket(`ws://192.168.254.18:8766`);

        signalingSocket.onopen = () => {
            console.log('Connected to WebSocket signaling server');
        };

        signalingSocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        signalingSocket.onclose = () => {
            console.log('WebSocket connection closed. Reconnecting...');
            if (peerConnection) {
                peerConnection.close();
                peerConnection = null;
            }
            setTimeout(connectWebSocket, 3000); // Reconnect after 3 seconds
        };

        signalingSocket.onmessage = async (event) => {
            console.log('Received message from signaling server:', event.data);
            const data = JSON.parse(event.data);

            if (data.answer) {
                console.log('Received SDP answer:', data.answer);
                await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
            } else if (data.iceCandidate) {
                console.log('Received ICE candidate:', data.iceCandidate);
                await peerConnection.addIceCandidate(new RTCIceCandidate(data.iceCandidate));
            }
        };
    }

    // Initial connection to the WebSocket server
    connectWebSocket();

    // Function to start screen sharing
    window.startScreenSharing = async () => {
        console.log('Starting screen sharing...');
        document.getElementById('startSharingScreen').style.display = 'none';
        document.getElementById('stopSharingScreen').style.display = 'inline';

        try {
            // Close existing peer connection if it exists
            if (peerConnection) {
                peerConnection.close();
                peerConnection = null;
            }
            // Capture the screen using the Screen Capture API
            screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
            console.log('Screen captured successfully');

            // Display the screen preview
            const videoElement = document.getElementById('screenShareVideo');
            videoElement.srcObject = screenStream;
            videoElement.style.display = 'block';

            // Create a new WebRTC peer connection
            peerConnection = new RTCPeerConnection({
                iceServers: [
                    { urls: 'stun:stun.l.google.com:19302' },  // Google's public STUN server
                    // You can add TURN servers if needed for better NAT traversal
                    //{ urls: 'turn:your-turn-server.com', username: 'user', credential: 'password' }
                ]
            });
            console.log('WebRTC peer connection created');

            // Add screen stream tracks to the peer connection
            screenStream.getTracks().forEach(track => {
                console.log('Adding track:', track.kind);
                peerConnection.addTrack(track, screenStream);
            });

            // Handle ICE candidates
            peerConnection.onicecandidate = ({ candidate }) => {
                if (candidate && signalingSocket.readyState === WebSocket.OPEN) {
                    console.log('Generated ICE candidate:', candidate);
                    signalingSocket.send(JSON.stringify({ 
                        iceCandidate: candidate.toJSON(), 
                        client_id: client_id 
                    }));
                } else {
                    console.error('WebSocket is not open. Cannot send ICE candidate.');
                }
            };

            // Create an SDP offer
            const offer = await peerConnection.createOffer();
            console.log('Created SDP offer:', offer);

            await peerConnection.setLocalDescription(offer);
            console.log('Set local description:', peerConnection.localDescription);

            // Send the SDP offer to the signaling server
            if (signalingSocket.readyState === WebSocket.OPEN) {
                signalingSocket.send(JSON.stringify({ 
                    type: 'offer', 
                    offer: peerConnection.localDescription, 
                    client_id: client_id 
                }));
                console.log('Sent SDP offer to signaling server');
            } else {
                console.error('WebSocket is not open. Cannot send SDP offer.');
            }

        } catch (error) {
            console.error('Error starting screen sharing:', error);
            if (error.name === 'NotFoundError') {
                alert('No screen capture source found. Please select a window or screen to share.');
            } else if (error.name === 'NotAllowedError') {
                alert('Permission denied. Please allow screen sharing.');
            } else {
                alert('An error occurred while starting screen sharing.');
            }
        }
    };

    // Function to stop screen sharing
    window.stopScreenSharing = () => {
        console.log('Stopping screen sharing...');
        document.getElementById('startSharingScreen').style.display = 'inline';
        document.getElementById('stopSharingScreen').style.display = 'none';

        if (screenStream) {
            screenStream.getTracks().forEach(track => track.stop()); // Stop all tracks
        }
        if (peerConnection) {
            peerConnection.close(); // Close the peer connection
        }
        document.getElementById('screenShareVideo').style.display = 'none'; // Hide the video preview
        console.log('Screen sharing stopped');
    };

    // Optional: Handle ICE connection state change
    peerConnection.oniceconnectionstatechange = () => {
        if (peerConnection.iceConnectionState === 'failed') {
            console.log('ICE connection failed');
            // Handle reconnection or retry logic here
            peerConnection.restartIce();
        }
    };
});
