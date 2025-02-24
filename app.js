let screenStream;
let screenPeerConnection;
const screenConstraints = { video: { mediaSource: 'screen' }, audio: false };  // تفعيل التقاط الشاشة فقط
const screenServers = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };  // خادم ICE
async function startScreenSharing() {
    try {
        // طلب التقاط الشاشة من المستخدم
        screenStream = await navigator.mediaDevices.getDisplayMedia(screenConstraints);

        // إعداد PeerConnection لبث الشاشة
        screenPeerConnection = new RTCPeerConnection(screenServers);

        // إضافة مسار الفيديو للتدفق
        screenStream.getTracks().forEach(track => screenPeerConnection.addTrack(track, screenStream));

        // التحقق من إعداد PeerConnection وإرسال إشارة العرض
        const offer = await screenPeerConnection.createOffer();
        await screenPeerConnection.setLocalDescription(offer);

        // إرسال العرض إلى Raspberry Pi
        socket.send(JSON.stringify({ offer: offer }));

        // عرض الفيديو على العميل (الذي يرسل الشاشة)
        const screenVideo = document.createElement('video');
        screenVideo.srcObject = screenStream;
        screenVideo.autoplay = true;
        document.body.appendChild(screenVideo);

        // إظهار زر إيقاف المشاركة
        document.getElementById('startSharingScreen').style.display = 'none';
        document.getElementById('stopSharingScreen').style.display = 'inline';

    } catch (err) {
        console.error('Error starting screen sharing:', err);
        alert('Failed to share screen. Please check your permissions.');
    }
}

function stopScreenSharing() {
    // إيقاف جميع مسارات الفيديو
    screenStream.getTracks().forEach(track => track.stop());

    // إغلاق PeerConnection
    screenPeerConnection.close();

    // إزالة الفيديو من الواجهة
    const screenVideo = document.querySelector('video');
    if (screenVideo) {
        screenVideo.remove();
    }

    // إعادة زر "Start Sharing Screen"
    document.getElementById('startSharingScreen').style.display = 'inline';
    document.getElementById('stopSharingScreen').style.display = 'none';
}

socket.onmessage = async (event) => {
    const message = JSON.parse(event.data);
    if (message.offer) {
        // تلقي عرض (Offer) من Raspberry Pi
        await handleOffer(message.offer);
    } else if (message.answer) {
        // تلقي إجابة (Answer)
        await handleAnswer(message.answer);
    } else if (message.iceCandidate) {
        // تلقي مرشح ICE
        await screenPeerConnection.addIceCandidate(new RTCIceCandidate(message.iceCandidate));
    }
};

async function handleOffer(offer) {
    // إعداد PeerConnection لاستقبال العرض
    screenPeerConnection = new RTCPeerConnection(screenServers);
    screenPeerConnection.ontrack = (event) => {
        const remoteVideo = document.getElementById('remoteVideo');
        remoteVideo.srcObject = event.streams[0];
    };

    // إعداد PeerConnection بالإجابة (Answer)
    await screenPeerConnection.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await screenPeerConnection.createAnswer();
    await screenPeerConnection.setLocalDescription(answer);

    // إرسال الإجابة (Answer)
    socket.send(JSON.stringify({ answer: answer }));
}
screenPeerConnection.onicecandidate = (event) => {
    if (event.candidate) {
        socket.send(JSON.stringify({ iceCandidate: event.candidate }));
    }
};


