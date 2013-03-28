function finishLogin(assertion) {
  $.post('/login', { assertion: assertion }, function(data, status, xhr) {
      console.log(arguments);
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

  if (navigator.mozApps) {
    $('#container').append('<a id="install-button" class="btn btn-primary offset4">Install</a>');
    $('#install-button').click(function() {
      navigator.mozApps.install("http://localhost:5000/static/manifest.webapp");
    });
  }
});
