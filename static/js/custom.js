$(function () {
	
	//$(".remove-user-trigger").click(remove-user );


	$("#add-user-form").submit(function(){
		$.ajax({
			url: "/entries?ajax=1",
			data: $(this).serializeArray(),
			method: "POST"
		}).done(function(data) {
			$("#add-user-form")[0].reset();
			$( "#table-entries" ).html(data);
		});

		return false;

	});

	$("#start-play-trigger").click(function() {
		var score = Number(prompt("Puntaje", "100"));
		var id = $(this).data("id");
		
		$.ajax({
			url: "/entries/" + id,
			data: { 'score':score, 'played':1, 'rewarded': 0},
			method: "PUT"
		}).done(function(data) {
			$( "#table-entries" ).html(data);
		});

	});

});

//global scope
function removeuser(id){
		//var id = $(this).data("id");
		$.ajax({
			url: "/entries/" + id,
			method: "DELETE"
		}).done(function(data) {
			$( "#table-entries" ).html(data);
		});
	}
