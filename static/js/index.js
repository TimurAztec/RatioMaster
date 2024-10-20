let translations = []

$(document).ready(function() {
	$('#loading-overlay').fadeOut();
	calculate();
	loadTranslations('en');

	$('#language-selector').change( function(val) { loadTranslations(val.currentTarget.value); });
	$('#chainring').change( function() { calculate(); });
	$('#sprocket').change( function() { calculate(); });
	$('#tire').change( function() { calculate(); });
	$('#ambidextrous').change( function() { calculate(); });
	$('[name=unit]').change( function(val) { 
		calculate();
		$('#avg-speed-unit').html(val.currentTarget.value == 'm' ? '(km/h)' : '(mph)');
	});

	$('#gpxFiles').on('change', function () {
		const files = $(this).prop('files');
		const fileList = $('#fileList');
		fileList.empty();

		if (files.length) {
			$.each(files, function (index, file) {
				fileList.append(`<div>${file.name}</div>`);
			});
		} else {
			fileList.append('<div>No files selected.</div>');
		}
	});

	$('#submitGpx').on('click', function() {
		$('#loading-overlay').fadeIn();
		const formData = new FormData();
		const files = $('#gpxFiles').prop('files');

		if (files.length === 0) {
			alert('Please select GPX files to upload.');
			return;
		}

		$.each(files, function(index, file) {
			formData.append('files', file);
		});
		formData.append('wheel_circumference', $('#tire').val());
		$.ajax({
			url: '/upload_gpx',
			type: 'POST',
			data: formData,
			processData: false,
			contentType: false,
			success: function(response) {
				$('#loading-overlay').fadeOut();
				alert('Files uploaded successfully! \nGear ratio set to recommended.');
				$('#chainring').val(response.optimal_gear_ratios[response.optimal_gear_ratios.length - 1][0]);
				$('#sprocket').val(response.optimal_gear_ratios[response.optimal_gear_ratios.length - 1][1]);
				calculate();
			},
			error: function(xhr, status, error) {
				alert('Error uploading files: ' + error);
			}
		});
	});
});

function calculateGCD(num1, num2) {
    while (num2 !== 0) {
        const remainder = num1 % num2;
        num1 = num2;
        num2 = remainder;
    }
    return num1;
}

function calculate() {
	let chainringT = parseInt($('#chainring').val());
	let sprocketT = parseInt($('#sprocket').val());
	let unit = $("input[name='unit']:checked").val();
	const ratio = Math.round(chainringT/sprocketT*100)/100;
	const tire = $('#tire').val();

	$('#ratio').html(ratio);

	let thisFactor = 1;
	let thisUnit = '';
	if ( unit == "m" ) {
		thisUnit = 'meters';
	} else {
		thisFactor = 0.0254;
		thisUnit = 'inches';
	}

	let development = ratio * (tire/1000);
	$('#development').html(Math.round(development*100/thisFactor)/100 + ' ' + thisUnit);

	const situations = [
		{ name: "Top speed", range: [120, 140] },
		{ name: "Fast Riding", range: [100, 120] },
		{ name: "Moderate Riding", range: [80, 110] },
		{ name: "Casual Riding", range: [70, 90] },
		{ name: "Hill Climbing", range: [40, 70] },
		{ name: "Steep hill climbing 💀", range: [30, 50] },
		{ name: "Long Distance Riding", range: [75, 85] },
		{ name: "Off-Road Riding", range: [65, 85] },
	];

	$('#speeds-table-body').empty();
	situations.forEach(situation => {
		const [minCadence, maxCadence] = situation.range;
		const averageCadence = (minCadence + maxCadence) / 2;

		const speedKMH = (averageCadence * development / 1000) * 60;
		const speedMPH = speedKMH * 0.621371;

		const newRow = `
			<tr>
				<td>${situation.name}</td>
				<td>${minCadence} - ${maxCadence}</td>
				<td>${unit == "m" ? speedKMH.toFixed(2) : speedMPH.toFixed(2)}</td>
			</tr>
		`;
		$('#speeds-table-body').append(newRow);
	});

	populateTable(ratio);
}

function generateGearCombinations(minRing, maxRing, minSprocket, maxSprocket) {
	const combinations = [];
	for (let ring = minRing; ring <= maxRing; ring++) {
		for (let sprocket = minSprocket; sprocket <= maxSprocket; sprocket++) {
			combinations.push({ ring, sprocket, ratio: (ring / sprocket).toFixed(2) });
		}
	}
	return combinations;
}

function populateTable(currentRatio, tolerance = 0.05) {
	const tableBody = $("#simmilar-ratios-table");
	tableBody.empty();

	const allCombinations = generateGearCombinations(28, 60, 11, 28);

	const filteredCombinations = allCombinations.filter(({ ratio }) => {
		return Math.abs(ratio - currentRatio) <= tolerance;
	});

	let row = $("<tr></tr>");
	filteredCombinations.forEach(({ ring, sprocket, ratio }, index) => {
		const cell = $(`<td title="${ratio}" onclick="changeGearRatio(${ring}, ${sprocket}, ${ratio})">${ring}×${sprocket}</td>`);
		row.append(cell);

		if ((index + 1) % 8 === 0) {
			tableBody.append(row);
			row = $("<tr></tr>");
		}
	});

	if (row.children().length > 0) {
		tableBody.append(row);
	}
}

function changeGearRatio(ring, sprocket, ratio) {
	$('#chainring').val(ring);
    $('#sprocket').val(sprocket);
	$('#ratio').text(ratio);
	calculate();
}

function loadTranslations(lang) {
	$.getJSON('static/locales/' + lang + '.json', function(translations) {
		translations = translations;
		$('[data-translate]').each(function() {
			var key = $(this).data('translate');
			$(this).text(translations[key]);
		});
	});
}

// function draw(){
	
// 	var canvas = document.getElementById('wheel');
// 	var lang = $("input[name='lang']:checked").val();
	

// 	if (canvas.getContext){
// 		var thispgcd=pgcd(r,s);
// 		var simp_den = r/thispgcd
// 		var sp = s/thispgcd;
// 		var posx = 80;
// 		var posy = 80;
// 		var ctx = canvas.getContext('2d');
// 		ctx.clearRect(0,0,300,300);

// 		// Roue
// 		ctx.beginPath();
// 		ctx.strokeStyle = "#333333";
// 		ctx.lineWidth=4;
// 		ctx.arc(posx,posy,72,0,Math.PI*2,true);
// 		ctx.stroke();
// 		ctx.beginPath();
// 		ctx.strokeStyle = "#AAAAAA";
// 		ctx.lineWidth=3;
// 		ctx.arc(posx,posy,67,0,Math.PI*2,true);
// 		ctx.stroke();

// 		// Rayons
// 		ctx.strokeStyle = "#BBBBBB";
// 		ctx.lineWidth=1;
// 		for (var i=0; i<32; i++) {
// 			ctx.beginPath();
// 			ctx.arc(posx,posy,67,i*(Math.PI*2/32),((i+0.2)*Math.PI*2/32),false);
// 			ctx.lineTo(posx,posy);
// 			ctx.stroke();
// 		}

// 		// Skid patchs
// 		ctx.strokeStyle = "#FF0055";
// 		ctx.lineWidth=8;
// 		for (var i=0; i<sp; i++) {
// 			ctx.beginPath();
// 			ctx.arc(posx,posy,70,i*(Math.PI*2/sp),((i+0.2)*Math.PI*2/sp),false);
// 			ctx.stroke();
// 		}

// 		if ( $('#a').attr('checked') && simp_den%2 > 0 ) {
// 			ctx.strokeStyle = "#0088FF";
// 			var offset = Math.PI/sp;
// 			for (var i=0; i<sp; i++) {
// 				ctx.beginPath();
// 				ctx.arc(posx,posy,70,i*(Math.PI*2/sp)+offset,((i+0.2)*Math.PI*2/sp)+offset,false);
// 				ctx.stroke();
// 			}
// 		}

// 		// Plateau et pignon
// 		cog(ctx,s,posx,posy);
// 		cog(ctx,r,posx+100,posy);

// 		// Chaine
// 		ctx.beginPath();
// 		ctx.strokeStyle = "#888888";
// 		ctx.lineWidth=2;
// 		ctx.moveTo(posx,posy-s/2);
// 		ctx.lineTo(posx+100,posy-r/2+2);
// 		ctx.arc(posx+100,posy,r/2-2,-Math.PI/2,Math.PI/2,false);
// 		ctx.lineTo(posx,posy+s/2);
// 		ctx.arc(posx,posy,s/2,Math.PI/2,-Math.PI/2,false);
// 		ctx.stroke();
// 	}
// }

// function cog(ctx,teeth,x,y) {
// 	ctx.beginPath();
// 	ctx.arc(x,y,teeth/2.5,0,Math.PI*2,true); // Cercle ext�rieur
// 	ctx.fillStyle = "#333333";
// 	ctx.fill();
// 	for (var i=0; i<teeth; i++) {
// 		ctx.beginPath();
// 		ctx.arc(x,y,teeth/2.5+2,i*(Math.PI*2/teeth),((i+0.5)*Math.PI*2/teeth),false);
// 		ctx.lineTo(x,y);
// 		ctx.fill();
// 	}
// 	for (var i=0; i<5; i++) {
// 		ctx.beginPath();
// 		ctx.fillStyle = "white";
// 		ctx.arc(x,y,(teeth-5)/3.5,i*(Math.PI*2/5),((i+0.7)*Math.PI*2/5),false);
// 		ctx.lineTo(x,y);
// 		ctx.fill();
// 	}
// } 
