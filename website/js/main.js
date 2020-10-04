function elab(img_id, deletehash){
  var API_LINK = "http://" + document.domain + ":5000/api/";

  $.ajax({
    dataType: "json",
    url: API_LINK + img_id,
    data: {
      "deletetoken": deletehash
    },
    timeout:30000,
    success: function(data) {
      stopLoading()
      displayResult(data)
    },
    error: function(xmlhttprequest, textstatus, message) {
        displayError("Error while processing the image. Our image-processing machine could be offline: please try again later.");
    }
  });
}

function startLoading(){
  $(".loading").show();
  $(".info_text").hide();
}

function stopLoading(){
  $(".loading").hide();
  $(".info_text").show();
}

function displayResult(data){
  $(".info_zone").hide();
  $(".error_zone").hide();
  $(".success_zone").show();
  $(".success_zone p .data_score").text((data.score*100).toFixed(2));
  $(".success_zone p .data_object").text(data.object);

  speak($(".success_zone p").text());
}

function displayError(error){
  stopLoading();
  $(".info_zone").hide();
  $(".error_zone").show();
  $(".success_zone").hide();
  $(".error_zone p").text(error);

  speak(error);
}

function speak(text){
  var msg = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.speak(msg);
}

$( document ).ready(function() {

  var CLIENT_ID = "cdf747392609b91";

  $("#image_selector").change(function() {
    startLoading();
    var reader = new FileReader();
    reader.onload = function(e) {
      var data = e.target.result.substr(e.target.result.indexOf(",") + 1, e.target.result.length);
      $.ajax({
        url: 'https://api.imgur.com/3/image',
        headers: {
          'Authorization': 'Client-ID ' + CLIENT_ID
        },
        type: 'POST',
        data: {
          'image': data,
          'type': 'base64'
        },
        success: function(response) {
          var link = response.data.link;
          var filename = link.substring(link.lastIndexOf("/")+1, link.length);
          var deletehash = response.data.deletehash;
          console.log("link: " + link);
          console.log("deletehash: " + deletehash);
          console.log("filename: " + filename);
          elab(filename, deletehash);
        },
        error: function() {
          displayError("Error while uploading the image. The image-hosting server could be offline: please try again later.");
        }
      });
    };
    reader.readAsDataURL(this.files[0]);
  });

});
