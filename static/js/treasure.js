var csrftoken = getCookie('csrftoken');
var answersList = [];
var submittedAnswer;


$(document).ready(function() {
  setupAjax();

});



function questionAnswered(){
  if (document.getElementById("radio-text").checked) {
    submittedAnswer = document.getElementById("answer-text").value;
    if (submittedAnswer != "") {
      makeAjaxCall();
    }
  } else if (answersList.length > 0) {
    checkAnswerList();
    makeAjaxCall();
  }
}

function checkAnswerList(){
  for (var i = 0; i < answersList.length; i++) {
    if (document.getElementById("radio-" + i).checked) {
      submittedAnswer = document.getElementById("answer-" + i).innerHTML;
      return;
    }
  }
}

function ajaxOutboundData(){

  var submitData = {
    'question': question,
    'answer': submittedAnswer,
    'user_id': user_id
  };
  return submitData;
}


function makeAjaxCall(){
  $.ajax({
      type: "POST",
      url: ajaxUrl,
      dataType: "json",
      data: ajaxOutboundData(),
      success: function(data) {
          questionData = JSON.parse(data.context);
          checkGameStatus();
        }

  });
}

function checkGameStatus(){
  if (questionData.game_over == true) {
    var gameOver = ""
    if (questionData.truth_percentage > 0.9) {
      gameOver += "<h2>You were too honest!</h2>"
    } else {
      gameOver += "<h2>You lied too much!</h2>"
    }
    gameOver += "<h3>The hunters worked out you found treasure.<br>"
    gameOver += "You're currently being tortured.</h3></span>"
    gameOver += '<input type="button" onclick="location.href=' + "'" + homeUrl + "'" + '" value="Play Again">'
    updateStyle('quiz-div', 'text-align: center;');
    updateContent('quiz-div', gameOver);
  } else {
    pushNewQuestion();
    pushAnswerList();
  }
}


function pushNewQuestion() {
  question = questionData.question
  updateContent('question1',question);
  document.getElementById('answer-text').value = '';
  document.getElementById('radio-text').checked = true;
}

function pushAnswerList() {
  answersList = questionData.answers_list
  var previousAnswers = ""
  for (var i = 0; i < answersList.length; i++) {
    previousAnswers += '<input type="radio" name="answers" id="radio-' + i
    previousAnswers += '"><span id="answer-' + i
    previousAnswers += '">' + answersList[i] + '</span><br>'
  }
  updateContent('previousAnswers', previousAnswers);
}

function updateContent(id,content) {
  document.getElementById(id).innerHTML = content;
}

function updateStyle(id,style) {
  document.getElementById(id).setAttribute("style",style);
}


// CSRF code
function getCookie(name) {
    var cookieValue = null;
    var i = 0;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (i; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function setupAjax() {
  $.ajaxSetup({
      crossDomain: false,
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type)) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });
}
