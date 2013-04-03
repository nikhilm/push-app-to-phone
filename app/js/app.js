function finishLogin(assertion) {
  $.post('/weblogin', { assertion: assertion }, function(data, status, xhr) {
      //window.location.reload();
  });
}

$(function() {
  navigator.id.watch({
    loggedInUser: null,
    onlogin: finishLogin,
    onlogout: function() {
      console.log("onlogout");
    }
  });

  $('#persona-signin').click(function() {
    navigator.id.request();
  });
});
