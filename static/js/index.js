$(document).ready(function() {
		$('.dialog').dialog({ autoOpen: false, modal: true });
		draw();

		$('#r').change( function() { draw(); });
		$('#s').change( function() { draw(); });
		$('#t').change( function() { draw(); });
		$('#a').change( function() { draw(); });
		$('[name=unit]').change( function() { draw(); });

        $('#gpxFiles').on('change', function () {
            const files = $(this).prop('files');
            const fileList = $('#fileList');
            fileList.empty(); // Clear existing file names
    
            if (files.length) {
                $.each(files, function (index, file) {
                    fileList.append(`<div>${file.name}</div>`); // Append each file name
                });
            } else {
                fileList.append('<div>No files selected.</div>'); // Message for no files
            }
        });

        $('#submitGpx').on('click', function() {
            const formData = new FormData();
            const files = $('#gpxFiles').prop('files');

            if (files.length === 0) {
                alert('Please select GPX files to upload.');
                return;
            }

            $.each(files, function(index, file) {
                formData.append('files', file); // Append each file to form data
            });
            formData.append('wheel_circumference', $('#t').val());
            // Send the files to the Flask route
            $.ajax({
                url: '/upload_gpx', // Adjust this to your Flask route
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    alert('Files uploaded successfully! \nGear ratio set to recommended.');
                    $('#r').val(response.optimal_gear_ratios[response.optimal_gear_ratios.length - 1][0]);
                    $('#s').val(response.optimal_gear_ratios[response.optimal_gear_ratios.length - 1][1]);
                    draw();
                },
                error: function(xhr, status, error) {
                    alert('Error uploading files: ' + error);
                    // Handle error response
                }
            });
        });
});

function pgcd(a,b) { return ( b == 0 ) ? a : pgcd(b, a%b); }

function draw(){
	var r = $('#r').val();
	var s = $('#s').val();
	var canvas = document.getElementById('wheel');
	var lang = $("input[name='lang']:checked").val();
	var unit = $("input[name='unit']:checked").val();

	if (canvas.getContext){
		var thispgcd=pgcd(r,s);
		var simp_den = r/thispgcd
		var sp = s/thispgcd;
		var posx = 80;
		var posy = 80;
		var ctx = canvas.getContext('2d');
		ctx.clearRect(0,0,300,300);

		// Roue
		ctx.beginPath();
		ctx.strokeStyle = "#333333";
		ctx.lineWidth=4;
		ctx.arc(posx,posy,72,0,Math.PI*2,true);
		ctx.stroke();
		ctx.beginPath();
		ctx.strokeStyle = "#AAAAAA";
		ctx.lineWidth=3;
		ctx.arc(posx,posy,67,0,Math.PI*2,true);
		ctx.stroke();

		// Rayons
		ctx.strokeStyle = "#BBBBBB";
		ctx.lineWidth=1;
		for (var i=0; i<32; i++) {
			ctx.beginPath();
			ctx.arc(posx,posy,67,i*(Math.PI*2/32),((i+0.2)*Math.PI*2/32),false);
			ctx.lineTo(posx,posy);
			ctx.stroke();
		}

		// Skid patchs
		ctx.strokeStyle = "#FF0055";
		ctx.lineWidth=8;
		for (var i=0; i<sp; i++) {
			ctx.beginPath();
			ctx.arc(posx,posy,70,i*(Math.PI*2/sp),((i+0.2)*Math.PI*2/sp),false);
			ctx.stroke();
		}

		if ( $('#a').attr('checked') && simp_den%2 > 0 ) {
			ctx.strokeStyle = "#0088FF";
			var offset = Math.PI/sp;
			for (var i=0; i<sp; i++) {
				ctx.beginPath();
				ctx.arc(posx,posy,70,i*(Math.PI*2/sp)+offset,((i+0.2)*Math.PI*2/sp)+offset,false);
				ctx.stroke();
			}
		}

		// Plateau et pignon
		cog(ctx,s,posx,posy);
		cog(ctx,r,posx+100,posy);

		// Chaine
		ctx.beginPath();
		ctx.strokeStyle = "#888888";
		ctx.lineWidth=2;
		ctx.moveTo(posx,posy-s/2);
		ctx.lineTo(posx+100,posy-r/2+2);
		ctx.arc(posx+100,posy,r/2-2,-Math.PI/2,Math.PI/2,false);
		ctx.lineTo(posx,posy+s/2);
		ctx.arc(posx,posy,s/2,Math.PI/2,-Math.PI/2,false);
		ctx.stroke();
	}

	$('#ratio').html( nformat( Math.round(r/s*100)/100, lang ) );

	var rsp = ( $('#a').attr('checked') && simp_den%2 > 0 ) ? sp*2 : sp;
	$('#skidpatch').html( rsp );

	var thisFactor = 1;
	var thisUnit = '';
	if ( unit == "m" ) {
		thisUnit = 'meters';
	} else {
		thisFactor = 0.0254;
		thisUnit = 'inches';
	}

	var dev = (r/s) * $('#t').val()/1000; // developpement en m�tres
	$('#dev').html( nformat( Math.round(dev*100/thisFactor)/100, lang ) + ' ' + thisUnit );

	var near = '<table><tr>';
	var ratio = r/s;
	var count = 0;
	for (var i=28; i<60; i++) {
		for (var j=9; j<24; j++) {
			if ( Math.abs(ratio - i/j) < ratio*0.02 ) {
				if ( count++ %8 == 0 ) { near = near + '</tr><tr>'; }
				near = near + '<td onclick="$(\'#r\').val(\'' + i + '\'); $(\'#s\').val(\''
					+ j + '\'); draw('+ i +',' + j + ');"'
					+ ' title="' + Math.round(i/j*100)/100 +'"'
					+'>' + i + '&times;' + j
					+ '</td>';
			}
		}
	}
	$('#near').html( near + '</tr></table>' );

	var speeds = '<table><tr>';
	var count = 0;
	var thisFactor = 1;
	var thisUnit = ' km/h';
	var thisUnit2 = '@';
	var thisUnit3 = ' rpm';
	if ( unit == "i" ) {
		thisFactor = 1.609;
		thisUnit = ' mph';
	}
	if ( lang == "fr" ) {
		//thisUnit2 = '&agrave; ';
		thisUnit2 = '';
		thisUnit3 = ' tr/mn';
	}
	for (var i=50; i<140; i= i+10) {
		if ( count++ %3 == 0 ) { speeds = speeds + '</tr><tr>'; }
		var cssclass = ( i== 90 ) ? ' class="rpm90"' : ''; 
		speeds = speeds + '<td' + cssclass +'>' + nformat( Math.round(dev*i/100*60/thisFactor)/10, lang )
			+ thisUnit + '</td><th' + cssclass + '>' + thisUnit2 + i + thisUnit3 + '</th>';
	}
	$('#speeds').html( speeds + '</tr></table>' );
}

function cog(ctx,teeth,x,y) {
	ctx.beginPath();
	ctx.arc(x,y,teeth/2.5,0,Math.PI*2,true); // Cercle ext�rieur
	ctx.fillStyle = "#333333";
	ctx.fill();
	for (var i=0; i<teeth; i++) {
		ctx.beginPath();
		ctx.arc(x,y,teeth/2.5+2,i*(Math.PI*2/teeth),((i+0.5)*Math.PI*2/teeth),false);
		ctx.lineTo(x,y);
		ctx.fill();
	}
	for (var i=0; i<5; i++) {
		ctx.beginPath();
		ctx.fillStyle = "white";
		ctx.arc(x,y,(teeth-5)/3.5,i*(Math.PI*2/5),((i+0.7)*Math.PI*2/5),false);
		ctx.lineTo(x,y);
		ctx.fill();
	}
} 

function nformat(num,lang) {
	var str = String(num);
	if ( lang == "fr" ) {
		return (str.replace(/\./g, ','));
	} else {
		return (str);
	}
}
