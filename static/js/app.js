$('.ui.dropdown')
 .dropdown()
;

function order(stock_id){
  var quantity = document.getElementById('order-'+ stock_id);
  window.location = '/order/'+ stock_id + '/' + quantity.value;
}