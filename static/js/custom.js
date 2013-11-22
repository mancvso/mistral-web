$(function () {


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

	/* Knockout bindings */
	var users = {
		waiting: ko.observableArray(),
		current: {
			id: ko.observable(),
		    name: ko.observable(),
		    score: ko.observable(),
		    lastname: ko.observable(),
		    rut: ko.observable(),
		    called: ko.observable()
		},
		next: {
			id: ko.observable(),
		    name: ko.observable(),
		    lastname: ko.observable()
		}
	}

	users.current.fullname = ko.computed( function(){
    	return users.current.name() + " " + users.current.lastname();
	});

	users.next.fullname = ko.computed( function(){
    	return users.next.name() + " " + users.next.lastname();
	});

	users.hasnext = function(){
		return users.waiting().length > 1;
	};

	users.current.clear = function(){
		users.current.id();
		users.current.name();
		users.current.score();
		users.current.lastname();
		users.current.rut();
		users.current.called();
	};

	users.isempty = function(){
		return users.waiting().length == 0;	
	};

	users.removeUser = function(user){
		$.ajax({
			url: "/usuarios/" + user.id + "?json=true&permament=true",
			method: "DELETE"
		}).done(function(data) {
			$("#add-user-form")[0].reset();
			users.current.clear();
			users.fetchAll();
		});
	};

	users.fetchAll = function(){
		// Cargamos sólo los que están a la espera
    	$.getJSON("/usuarios?json=true&scope", function(data) {
    		//console.log(data);
    		if(data.status == "OK" && data.data != null){
    			// El primero sería también current
    			users.current.id(data.data[0].id);
    			users.current.name(data.data[0].name);
    			users.current.score(data.data[0].score);
    			users.current.lastname(data.data[0].lastname);
    			users.current.rut(data.data[0].rut);
    			users.current.called(data.data[0].called);
    			// Next
    			users.waiting(data.data);

    			if(users.hasnext() == true){
    				//console.log(data.data[1]);

    				users.next.id(data.data[1].id);
    				users.next.name(data.data[1].name);
    				users.next.lastname(data.data[1].lastname);
    			}

    		} else {
    			users.waiting([]);
    		}
		});
	}



    /* Long pooling  */
	function poll(){
	    $.ajax({ url: "/usuarios/next?json=true", success: function(data){
	    	//console.log(data);
	    	if(data.status == "OK" && data.data != null){
	    	//console.log("CUR:" + data.data[0].id + " PREV:" + users.current.id() + " NSCORE:" + data.data[0].score);
	    		if(data.data[0].id != users.current.id()){
	    			// recargar lista de usuarios
	        		users.fetchAll();
	    		} else {
	    			users.current.score(data.data[0].score);
	    		}

	    	}

	    }, dataType: "json", complete: poll, timeout: 3000 });
	}


    /* Knockout fetch */
    ko.applyBindings(users);
    users.fetchAll();
	// activar long-pooling
	//poll();



});
    

//global scope

