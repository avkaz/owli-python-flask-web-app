document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);


    // Set default room
    let room = "100000"


    let resultsContainer = document.getElementById('bubbles');


    let readyButton = document.getElementById('ready_button');
    let showScore = document.getElementById('show_score');
    
    let chartContainer = document.getElementById("chart-container");
    let pictureContainer = document.getElementById("question_picture_container")

    let questionContainer = document.getElementById("question-container");




    // function that shows bar charst with correct answers and change the height of bars
    let showBar = () => {

        //calculating the percenatage of answers to set the height of bars in the bar chart
        




        
        let answer1Percentage = Math.round((answer1Counter / TotalClicks) * 100);
        if (isNaN(answer1Percentage)) {
            answer1Percentage = 0;
          }
        let answer2Percentage = Math.round((answer2Counter / TotalClicks) * 100);
        if (isNaN(answer2Percentage)) {
            answer2Percentage = 0;
          }
        let answer3Percentage = Math.round((answer3Counter / TotalClicks) * 100);
        if (isNaN(answer3Percentage)) {
            answer3Percentage = 0;
          }
        let answer4Percentage = Math.round((answer4Counter / TotalClicks) * 100);
        if (isNaN(answer4Percentage)) {
            answer4Percentage = 0;
          }
        pictureContainer.style.display="none"
        chartContainer.style.display="flex";
        if (correct_choices.includes(document.getElementById("answer1").innerHTML)){
          document.getElementById("bar-1").style.opacity="1";
          document.getElementById("cross_mark1").style.display="none"
          document.getElementById("check_mark1").style.display="inline"
        }
        if (correct_choices.includes(document.getElementById("answer2").innerHTML)){
          document.getElementById("bar-2").style.opacity="1";
          document.getElementById("cross_mark2").style.display="none"
          document.getElementById("check_mark2").style.display="inline"
        }
        if (correct_choices.includes(document.getElementById("answer3").innerHTML)){
          document.getElementById("bar-3").style.opacity="1";
          document.getElementById("cross_mark3").style.display="none"
          document.getElementById("check_mark3").style.display="inline"
        }
        if (correct_choices.includes(document.getElementById("answer4").innerHTML)){
          document.getElementById("bar-4").style.opacity="1";
          document.getElementById("cross_mark4").style.display="none"
          document.getElementById("check_mark4").style.display="inline"
        }
        //setting the height of bars
        document.getElementById("bar-1").style.height += answer1Percentage+5 + "%";//default height is 5%, that made in order to see answers that were not chosen
        document.getElementById("bar-2").style.height += answer2Percentage+5 + "%";
        document.getElementById("bar-3").style.height += answer3Percentage+5 + "%";
        document.getElementById("bar-4").style.height += answer4Percentage+5 + "%";

        //setting spans of bars
        document.getElementById('span-1').innerHTML = answer1Percentage + "%";
        document.getElementById('span-2').innerHTML = answer2Percentage + "%";
        document.getElementById('span-3').innerHTML = answer3Percentage + "%";
        document.getElementById('span-4').innerHTML = answer4Percentage + "%";

      }



    //when user connects
    socket.on("connect", () => {
        
        // Join room
        let newRoom = session;
        leaveRoom(room);
        joinRoom(newRoom);
        room = newRoom;
    });

    // When the user disconnects from the server
    socket.on("disconnect", () => {
        leaveRoom(room)
    });

    function joinRoom(room) {

        // Join room
        socket.emit('join', {'username': username, 'room': room});
    }

    function leaveRoom(room) {

        // leave room
        socket.emit('leave', {'username': username, 'room': room});
    }

    //answers counter ///// when user click on the answer button, function count the click and sum all clicks
    const answerButtons = document.querySelectorAll('#answer1, #answer2, #answer3, #answer4');
    const clickCounter = document.getElementById('click_counter');
    let TotalClicks = 0;
    let answer1Counter = 0;
    let answer2Counter = 0;
    let answer3Counter = 0;
    let answer4Counter = 0;
    
    answerButtons.forEach(button => {
      button.addEventListener('click', function() {
        if(username !=="None"){
          socket.emit('click', {'answerId': button.id, 'room': room});
        };
      });
    });
    
    socket.on('updateCounter', (data) => {
      counterObject = data.counter;
      TotalClicks  = counterObject['total'];
      answer1Counter = counterObject['answer1'];
      answer2Counter = counterObject['answer2'];
      answer3Counter = counterObject['answer3'];
      answer4Counter = counterObject['answer4'];
      
      clickCounter.innerText = TotalClicks;
      console.log(`Clicks for answer1: ${answer1Counter}`);
      console.log(`Clicks for answer2: ${answer2Counter}`);
      console.log(`Clicks for answer3: ${answer3Counter}`);
      console.log(`Clicks for answer4: ${answer4Counter}`);
    });

    // document.querySelector("#next_question").style.display = 'block';

    // when user click on ready button
    readyButton.addEventListener('click', function() {
        socket.emit('block_buttons',room);
        showScore.style.display ="block";
        readyButton.style.display = 'none'
        document.getElementById('answer1').disabled = true;
            document.getElementById('answer2').disabled = true;
            document.getElementById('answer3').disabled = true;
            document.getElementById('answer4').disabled = true;
            clearInterval(intervalId);
        document.getElementById('question_timer').style.display = 'none'
        clickCounter.style.display = 'none'
        showBar()
      });



    // when user click on showScore button
    showScore.addEventListener('click', function() {
        showScore.style.display ="none";
        document.querySelector("#next_question").style.display = 'block';
        document.querySelector("#inherit_score").style.display = 'block';
        chartContainer.style.display="none";
        questionContainer.style.display="none";
        console.log('showscore ok')
        socket.emit('answer',{'session':session, 'room':room, 'question_index': question_index});

    })


    // next question timer

    const timerDiv = document.getElementById("timer");
    let timerInterval;

    document.querySelector("#next_question").onclick = () => {
        history.pushState({}, "", "/");
        if (document.getElementsByName("results").length > 0){
            socket.emit("nextQuestion",{'session':session, 'room':room, 'quizlen':quizlen, 'question_index': question_index});
            } else {
        // Show the timer for 5 seconds
            let seconds = 3;
            timerDiv.classList.add("active");
            timerDiv.innerText = seconds;
    
            timerInterval = setInterval(() => {
                seconds--;
                timerDiv.innerText = seconds;
                if (seconds === 1) {
                    clearInterval(timerInterval);
                    timerDiv.innerText = "Get Ready...";
                    setTimeout(() => {
                        timerDiv.innerText = "Go!";
                        setTimeout(() => {
                            socket.emit("nextQuestion",{'session':session, 'room':room, 'quizlen':quizlen, 'question_index': question_index});
                        }, 1000);
                    }, 1000);
                }
            }, 1000);

        };
    };



        socket.on("redirect", (redirect) => {
        if (room === redirect.currentroom){
            window.location.href = redirect.url;
        };
    });


    //question timer
    let countdown = duration;
    let timerElement = document.getElementById('question_timer');
    let intervalId = setInterval(function() {
        countdown--;
        timerElement.innerHTML = countdown ;
        if (countdown === 10) {
            timerElement.style.color = 'orange';
        }
        if (countdown === 5) {
            timerElement.style.color = 'red';
            timerElement.style.fontSize = '7rem';
            setInterval(function() {
                timerElement.style.color = timerElement.style.color === 'red' ? '#1EBBD7' : 'red';
            }, 500);
        }
        if (countdown === 0) {
            document.getElementById('answer1').disabled = true;
            document.getElementById('answer2').disabled = true;
            document.getElementById('answer3').disabled = true;
            document.getElementById('answer4').disabled = true;
            clearInterval(intervalId);
            showScore.style.display ="block";
            readyButton.style.display = 'none'
            document.getElementById('question_timer').style.display = 'none'
            socket.emit('block_buttons',room);
            clickCounter.style.display = 'none'
            showBar()

        }
    }, 1000);
    
    
socket.on('block_buttons',()=>{
    document.getElementById('answer1').disabled = true;
    document.getElementById('answer2').disabled = true;
    document.getElementById('answer3').disabled = true;
    document.getElementById('answer4').disabled = true;
})

  socket.on('results', (results) => {
    users = results.users
    scores = results.score
    resultsContainer.innerHTML = '';
    for (let i = 0; i < results.score.length; i++) {
        let user = users[i];
        let score = scores[i];
        let bubble = document.createElement("div");
        bubble.classList.add("bubble")
        let place = document.createElement("span");
        place.classList.add("place");
        place.innerText = i+1
        let name = document.createElement("span");
        name.classList.add("name");
        name.innerText = user
        let scoreEl = document.createElement("span");
        scoreEl.classList.add("score");
        scoreEl.innerText = score
        bubble.appendChild(place)
        bubble.appendChild(scoreEl)
        bubble.appendChild(name)
        resultsContainer.appendChild(bubble)
      }
  });

})

