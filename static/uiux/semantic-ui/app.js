

//activate dropdowns
$('.ui.dropdown').dropdown();

//drop down for selecting age group

$('.ui.normal.dropdown')
  .dropdown({
    maxSelections: 3
  })
;
$('.ui.special.dropdown')
  .dropdown({
    useLabels: false,
    maxSelections: 3
  })
;

$('.ui.dropdown').dropdown();



$('.booking').on('click', function(){
  $('#modal1')
    .modal({
      inverted: true
    }).modal('show');
});

$('.profile').on('click', function(){
$('#modal2')
  .modal('show')
});

$('.tabular.menu .item').tab();





$('#age-info')
  .dropdown({
  	onChange: function(val){
      var age = val;
      var gender = $('#gender').val();
      getSymptoms(age,gender);
    }
  });

//gender selection radio buttons
$('#gender-info')
   .dropdown({
    onChange: function(val){
      var gender = val;
      var age = $('#who').val();
      getSymptoms(age,gender);
    }
});

$('#diagnosis').on('click','.title',function(e){
  $('.toBeHidden').addClass('hidden');
  $(this).find($('.content').addClass('active'));
  $(this).find($('p').removeClass('hidden').addClass('visible'));
});

function getSymptoms(age,gender){

  $.ajax({
    method: "POST",
    url: "http://localhost/kaizen/utano/app/search/here/",
    data: {gender: gender, age: age },
    success: function(data){
    data = JSON.parse(data);

    $('.symptoms-list').empty();

    console.log(data['hits']['hits'].length);

    for (i = 0; i < data['hits']['hits'].length - 1; i++) {
    if(i==2 || i==5){
      i +=1;
    } 
    console.log(data['hits']['hits'][i]['_source']['profile'][gender][age]);
    var results = data['hits']['hits'][i]['_source']['profile'][gender][age];
    
    results.forEach(function(symptom) {
      var button = "<div class='symptoms-button'><button class='ui right basic button' value='"+symptom+"'>"
      +symptom+"</button><br/></div>";
      $('.symptoms-list').append(button);
    });
    }
  }
});
}

function getDiagnosis(endpoint, symptoms){

  $.ajax({
    method: "POST",
    url: "http://localhost/kaizen/utano/app/search/get/",
    data: {endpoint: endpoint, symptoms: symptoms}, 
    success: function(data){
      data = JSON.parse(data);
      $('#diagnosis').empty();
    for (i = 0; i < data['hits']['hits'].length; i++) {


    var accordion ="<div class='ui styled accordion'>";

    var title = data['hits']['hits'][i]['_source']['title'];
    var brief = data['hits']['hits'][i]['_source']['brief'];
    var sTIclass =  data['hits']['hits'][i]['_source']['brief'];
    var treatment = data['hits']['hits'][i]['_source']['brief'];
    var type = data['hits']['hits'][i]['_source']['type'];
    var test = data['hits']['hits'][i]['_source']['test'];
    var lifelong = data['hits']['hits'][i]['_source']['lifelong'];
    var lifethreatenging = data['hits']['hits'][i]['_source']['life-threatening'];

    var title = "<div class='title'><i class='dropdown icon'></i>"+title+"</div>";
    var content = "<div class='content'><h5><p class='transition hidden toBeHidden'>";
    content = content +brief+"</p></h5><p><a href='http://localhost/kaizen/utano/app/find/profile/'>Get help about treatment</a></p></div>";

    var display = accordion+title+content+"</div>";

    //var button = "<div class='ui secondary segment symptoms-button'>"+results+"</div>";
      $('#diagnosis').append(display);
    }
    }
  });
}



//button click event that is used by user to select symptoms.
$('.symptoms-list').on('click','.symptoms-button',function(e){
    e.preventDefault(); 
    var button = $(this).index();
    console.log(button);
    $(this).hide();
    var symptom = "<div class='ui label'>"+$(this).children([0]).val()+"<i class='delete icon remove' button="+button+"></i></div>";
    $('div#selected-symptoms').append(symptom);
    
    var symptoms = "";
    $('div#selected-symptoms').children('div').each(function(){
        symptoms += $(this).text()+" ";
    });
    var gender = $('#gender').val();
    var age = $('#who').val();
    getDiagnosis(gender+"."+age,symptoms);
  });


//button click event that is used by user to remove selected sysmptoms.
 $('#selected-symptoms').on('click', '.remove', function(){
 	console.log($(this).attr('button'));
 		$('.symptoms-list').children('div').eq($(this).attr('button')).show();
 		$(this).parent().remove();
    var symptoms = "";
    $('div#selected-symptoms').children('div').each(function(){
        symptoms += $(this).text()+" ";
    });
    var gender = $('#gender').val();
    var age = $('#who').val();
    getDiagnosis(gender+"."+age,symptoms);
 });


