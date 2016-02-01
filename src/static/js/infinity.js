/* Project specific Javascript goes here. */

try{
  setTimeout(function(){
    if($ && $.fn && $.fn.select2){
      $.fn.select2.defaults.allowClear = true;  
    }
  },
  300)
}catch(e){}

$(function() {
  $("#id_personal").change(function() {$("#div_id_sharewith").toggle()});

  if ($("#id_personal").is(":checked")) {
    // Show if Personal checkbox is checked
    $("#div_id_sharewith").show();
  }
});

$(function() {
  $("#id_is_link").change(function() {$("#div_id_url").toggle()});

  if ($("#id_is_link").is(":checked")) {
    // Show url box if is_link checkbox is checked
    $("#div_id_url").show();
  }
});

$(function(){

    // Scroll screen horizontally by one screen
    $('#scroll_arrowleft').on("click",function(event){
      $( "div.row-horizon" ).scrollLeft( -$(window).width() );
			event.preventDefault();
    });

    $('#scroll_arrowright').on("click",function(event){
      $( "div.row-horizon" ).scrollLeft( $(window).width() );
			event.preventDefault();
    });
});
