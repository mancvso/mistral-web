$(function () {
	
	//$(".remove-user-trigger").click(remove-user );


	$("#add-user-form").submit(function(e){
		e.preventDefault();

		$.ajax({
			url: "/usuarios?json=true",
			data: $(this).serializeArray(),
			method: "POST"
		}).done(function(data) {
			$("#add-user-form")[0].reset();
			users.fetchAll();
		});

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

	/* Knockout bindings */
	var users = {
		waiting: ko.observableArray(),
		current: {
			id: ko.observable(),
		    name: ko.observable(),
		    score: ko.observable(),
		    lastname: ko.observable(),
		    rut: ko.observable()
		},
		next: {
			id: ko.observable(),
		    name: ko.observable()
		}
	}

	users.current.fullname = ko.computed( function(){
    	return users.current.name() + " " + users.current.lastname();
	});

	users.hasnext = function(){
		return users.waiting().length > 1;
	};

	users.hasnext = function(){
		return users.waiting().length == 0;	
	};

	users.removeUser = function(user){
		$.ajax({
			url: "/usuarios/" + user.id + "?json=true",
			method: "DELETE"
		}).done(function(data) {
			$("#add-user-form")[0].reset();
			users.fetchAll();
		});
	};

	users.fetchAll = function(){
		// Cargamos sólo los que están a la espera
    	$.getJSON("/usuarios?json=true&unscored=true", function(data) {
    		//console.log(data);
    		if(data.status == "OK" && data.data != null){
    			// El primero sería también current
    			users.current.id(data.data[0].id);
    			users.current.name(data.data[0].name);
    			users.current.score(data.data[0].score);
    			users.current.lastname(data.data[0].lastname);
    			users.current.rut(data.data[0].rut);
    			// Next
    			users.waiting(data.data);

    			if(users.hasnext() == true){
    				console.log(data.data[1]);

    				users.next.id(data.data[1].id);
    				users.next.name(data.data[1].name);
    			}

    		} else {
    			users.waiting([]);
    		}
		});
	}


    /* Knockout fetch */
    ko.applyBindings(users);
    users.fetchAll();


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

