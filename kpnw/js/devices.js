$(document).ready(function(){
  //Click the entire tr
  $("#dev-table tbody tr[data-link]").click(function(){
    window.location.href = $(this).data('link');
  });
  //Filter
  var filter = $("#filter");
  if( filter.length !== 0){
    $("#filter").keyup(function () {
      var filter = $(this).val(), count = 0;
      $("#dev-table tr").each(function () {
        if ($(this).find("a:first").text().search(new RegExp(filter, "i")) < 0) {
          $(this).addClass("hidden");
        } else {
          $(this).removeClass("hidden");
          count++;
        }
      });
      $("#filter-count").text(count);
    });
  }
});