$('form input[type=checkbox]').click ( function(){
    var $this = $(this);
    if (this.checked)
    { $(this).parent().addClass("highlight"); }
    else
    { $(this).parent().removeClass("highlight");  }
});