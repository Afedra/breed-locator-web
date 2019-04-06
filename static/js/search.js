$(function () {
  $(".breed-results li").click(function () {
    var breed = $(this).attr("breed-id");
    location.href = "/breeds/" + breed + "/";
  });

  $(".questions-results li").click(function () {
    var question = $(this).attr("question-id");
    location.href = "/questions/" + question + "/";
  });

});