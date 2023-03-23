document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Set default room
    let room = "100000"

    // Get references to message container, user container, and message input field
    let messageContainer = document.querySelector(".messages");
    let userContainer = document.querySelector(".users")
    let messageInput = document.getElementById("messageInput");

    // When user connects to the websocket
    socket.on("connect", () => {


        // Join room
        let newRoom = session;
        leaveRoom(room);
        joinRoom(newRoom);
        room = newRoom;
    });

    // When the user disconnects from the server
    socket.on("disconnect", () => {
        leave(room);
    });

    messageInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault(); // prevent form submission
            let message = {
                'msg': messageInput.value,
                'username': username,
                'room': room
            };
            socket.send(message);
        
            // Create a new message element for the sent message
            let newMessage = document.createElement("div");
            newMessage.classList.add("message", "sent");
            // Create a new p element to display the message text
            let messageElement = document.createElement("p");
            messageElement.textContent = message.msg;
            // Append the message element to the new message element
            newMessage.appendChild(messageElement);
            // Append the new message element to the message container element
            messageContainer.appendChild(newMessage);
        
            // Clear the message input field
            messageInput.value = "";
        }
    });
    

// Send message when send button is clicked
document.querySelector("#sendButton").onclick = () => {
    let message = {
        'msg': messageInput.value,
        'username': username,
        'room': room
    };
    socket.send(message);

    // Create a new message element for the sent message
    let newMessage = document.createElement("div");
    newMessage.classList.add("message", "sent");
    // Create a new p element to display the message text
    let messageElement = document.createElement("p");
    messageElement.textContent = message.msg;
    // Append the message element to the new message element
    newMessage.appendChild(messageElement);
    // Append the new message element to the message container element
    messageContainer.appendChild(newMessage);

    // Clear the message input field
    messageInput.value = "";
};

    // Display received message in message container
    socket.on('message', (message) => {
        if (message.room === room) {
            if (username !==message.username){
            // Create a new message element
            let newMessage = document.createElement("div");
            newMessage.classList.add("message", "received");
            // Create a new span element to display the message sender
            let senderElement = document.createElement("span");
            senderElement.classList.add("sender");
            senderElement.textContent = message.username;
            // Create a new p element to display the message text
            let messageElement = document.createElement("p");
            messageElement.textContent = message.msg;
            // Append the sender and message elements to the new message element
            newMessage.appendChild(senderElement);
            newMessage.appendChild(messageElement);
            // Append the new message element to the message container element
            messageContainer.appendChild(newMessage);
        }
        }

 





    });

    // Display newly joined user in user container
    socket.on('userJoined', (user) => {
        if(user!=="None"){
            let newUserElement = document.createElement('span');
            newUserElement.classList.add("user");
            newUserElement.innerText = user
            userContainer.appendChild(newUserElement);
        };
    });

    // Join a room
    function joinRoom(room) {
        socket.emit('join', {
            'username': username,
            'room': room
        });
    }

    // Leave a room
    function leaveRoom(room) {
        socket.emit('leave', {
            'username': username,
            'room': room
        });
    }

    // Countdown timer functionality
    const timerDiv = document.getElementById("timer");
    const QRCode = document.getElementById("qr_code");
    const startBtn = document.getElementById("start_quiz_Button");
    let timerInterval;

    document.querySelector("#start_quiz_Button").onclick = () => {
        history.pushState({}, "", "/");
        // Show the timer for 5 seconds
        let seconds = 3;
        QRCode.classList.add("hidden")
        startBtn.classList.add("hidden")
        timerDiv.classList.add("active");
        timerDiv.innerText = seconds;

        // Start the timer and emit startQuiz event after 3 seconds
        timerInterval = setInterval(() => {
            seconds--;
            timerDiv.innerText = seconds;
            if (seconds === 3) {
                timerDiv.style.color = "orange";
            }
            if (seconds === 1) {
                clearInterval(timerInterval);
                timerDiv.innerText = "Get Ready...";
                timerDiv.style.color = "orange";
                setTimeout(() => {
                    timerDiv.innerText = "Go!";
                    timerDiv.style.color = "red";
                    setTimeout(() => {
                        socket.emit("startQuiz", {
                            'session': session,
                            'room': room
                        });
                    }, 1000);
                }, 1000);
            }
        }, 1000);
        
    };

    // Redirect to quiz page after quiz is started
    socket.on("redirect", (redirect) => {
        if (room === redirect.currentroom) {
            window.location.href = redirect.url;
        };
    });

});
