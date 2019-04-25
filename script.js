var SpeechRecognition = window.webkitSpeechRecognition;
  
var recognition = new SpeechRecognition();

var da_counts = [0,0,0];
var num_words = 0;
var all_text = ""

recognition.continuous = true;

recognition.onresult = function(event) {

  var current = event.resultIndex;

  var transcript = event.results[current][0].transcript;
  all_text += ";" + transcript
  var classname = classify(transcript)

  var array = transcript.split(' ');
  var filtered = array.filter(function (el) {
    return el != "";
  });
  var numwords = filtered.length;

  num_words += numwords
  updateFeedback();
  
};

recognition.onstart = function() { 
  console.log('Voice recognition is ON.');
}

recognition.onspeechend = function() {
  console.log('No activity.');
  recognition.stop();
  setTimeout(
    function() {
      recognition.start();
      console.log("speech started")
    }, 500);
}

recognition.onerror = function(event) {
  if(event.error == 'no-speech') {
    console.log('Try again.');  
  recognition.stop();
  setTimeout(
    function() {
      recognition.start();
      console.log("speech started")
    }, 500);
  }
}

function startMeeting() {
  recognition.start();
}

function stopMeeting() {
  recognition.stop();
  sendDataToServer();
}

function resetMeeting() {
  da_counts = [0,0,0];
  num_words = 0;
  all_text = "";
  updateFeedback();
}

function updateFeedback() {
  document.getElementById("wordcount").innerHTML=num_words
  var num_da = da_counts[0] + da_counts[1] + da_counts[2]
  if (num_da < 1) {
    num_da = 1
  }
  num_da = 1.0*num_da
  results_chart.data.datasets[0].data = [100*da_counts[0]/num_da,100*da_counts[1]/num_da,100*da_counts[2]/num_da];
  results_chart.update();
}

function classify(sentence) {
  model.classify([sentence])
  .then(predictions => {
    //0:is,1:other,2:su
    var ind_mapping = [0,2,1]
    var preds = []
    var maxi = 0
    var maxv = 1

    for(var i = 0; i < 3; i++) {
      if (predictions[i].results[0].probabilities[0] < maxv){
        maxi = i
        maxv = predictions[i].results[0].probabilities[0]
      }
      console.log(predictions[i].results[0].probabilities[0])
      console.log("--")
    }
    var prediction = ind_mapping[maxi]
    da_counts[prediction] += 1
    updateFeedback();
    return true;
  });
}

function sendDataToServer() {
  var apiURL = "https://script.google.com/macros/s/AKfycbzSCe4rHKE10Hl2RyK_jvKN-_akuSnTKSenbfna9JKAeSMxTExu/exec?";
  var d = new Date();
  var n = d.getTime();
  apiURL += "timest="+n;
  apiURL += "&transcript="+encodeURI(all_text);
  apiURL += "&information_sharing="+da_counts[0];
  apiURL += "&shared_understanding="+da_counts[1];
  apiURL += "&other="+da_counts[2];
  apiURL += "&nwords="+num_words;
  const Http = new XMLHttpRequest();
  const url=apiURL;
  Http.open("GET", url);
  Http.send();
  Http.onreadystatechange=(e)=>{
    console.log(Http.responseText)
  }
}

const threshold = 0.7;
const labelsToInclude = ["information_sharing","shared_understanding","other"];
var model;

toxicity.load(threshold, labelsToInclude).then(modelz => {
  model = modelz
});