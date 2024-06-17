<!DOCTYPE html>
<html>
<head>
    <title>Lamp Control</title>
</head>
<body>
    <h1>Control the Lamp</h1>
    <button onclick="controlLamp('on')">Turn On</button>
    <button onclick="controlLamp('off')">Turn Off</button>

    <script>
        function controlLamp(action) {
            fetch('https://randomsubdomain.ngrok.io/control', {  // Use ngrok HTTPS URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: 'action=' + action
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    alert('Lamp ' + action);
                } else {
                    alert('Error controlling the lamp');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error controlling the lamp');
            });
        }
    </script>
</body>
</html>
