let translations = []
let resultsChart;

$(document).ready(function() {
	const hasVisited = Boolean(localStorage.getItem('hasVisited'));
    const fileInput = $('#files');
    const fileList = $('#fileList');
    const dataTransfer = new DataTransfer();

	if (!hasVisited) {
		const defaultUserLang = navigator.language || navigator.languages[0];
		const lang = defaultUserLang.startsWith('uk') ? 'ua' : 'en';
		localStorage.setItem('hasVisited', true);
		localStorage.setItem('lang', lang);
	}

	if (localStorage.getItem('lang')) {
		$('#language-selector').val(localStorage.getItem('lang'));
	}

	$('#loading-overlay').fadeOut();
	loadTranslations($('#language-selector').val());

	$('#language-selector').change( function(val) {
		const lang = val.currentTarget.value;
		localStorage.setItem('lang', lang);
		loadTranslations(lang);
	});
	$('#chainring').change( function() { calculate(); });
	$('#sprocket').change( function() { calculate(); });
	$('#tire').change( function() { calculate(); });
	$('#ambidextrous').change( function() { calculate(); });
	$('[name=unit]').change( function(val) { 
		calculate();
		$('.speed-unit').html(val.currentTarget.value == 'm' ? '(km/h)' : '(mph)');
	});

	$("#cadence-dialog").dialog({
        autoOpen: false,
        modal: true,
		autoOpen: false,
		draggable: false,
    	resizable: false,
		position: { my: "center", at: "center", of: window },
		open: function() {
			$(this).parent().css({
				position: "fixed",
				top: "50%",
				left: "50%",
				transform: "translate(-50%, -50%)",
				maxWidth: "90%",
				minWidth: "300px",
			});
	
			$(".ui-dialog-titlebar-close").html("&#10005;").css({
				fontSize: "20px", 
				color: "#fff", 
				backgroundColor: "#f44336",
				padding: "5px", 
				borderRadius: "50%",
			});
	
			$(".ui-dialog-content").css({
				padding: "20px",
				color: "#333",
				fontFamily: "Arial, sans-serif"
			});
		},
		close: function() {
			$(this).find(".ui-dialog-content").html("");
		},
        width: 400
    });
    $("#gear-ratio-dialog").dialog({
        autoOpen: false,
        modal: true,
		autoOpen: false,
		draggable: false,
    	resizable: false,
		position: { my: "center", at: "center", of: window },
		open: function() {
			$(this).parent().css({
				position: "fixed",
				top: "50%",
				left: "50%",
				transform: "translate(-50%, -50%)",
				maxWidth: "90%",
				minWidth: "300px",
			});
	
			$(".ui-dialog-titlebar-close").html("&#10005;").css({
				fontSize: "20px", 
				color: "#fff", 
				backgroundColor: "#f44336",
				padding: "5px", 
				borderRadius: "50%",
			});
	
			$(".ui-dialog-content").css({
				padding: "20px",
				color: "#333",
				fontFamily: "Arial, sans-serif"
			});
		},
		close: function() {
			$(this).find(".ui-dialog-content").html("");
		},
        width: 400
    });
    $("#skid-patches-dialog").dialog({
        autoOpen: false,
        modal: true,
		autoOpen: false,
		draggable: false,
    	resizable: false,
		position: { my: "center", at: "center", of: window },
		open: function() {
			$(this).parent().css({
				position: "fixed",
				top: "50%",
				left: "50%",
				transform: "translate(-50%, -50%)",
				maxWidth: "90%",
				minWidth: "300px",
			});
	
			$(".ui-dialog-titlebar-close").html("&#10005;").css({
				fontSize: "20px", 
				color: "#fff", 
				backgroundColor: "#f44336",
				padding: "5px", 
				borderRadius: "50%",
			});
	
			$(".ui-dialog-content").css({
				padding: "20px",
				color: "#333",
				fontFamily: "Arial, sans-serif"
			});
		},
		close: function() {
			$(this).find(".ui-dialog-content").html("");
		},
        width: 400
    });
    $("#gear-inches-dialog").dialog({
        autoOpen: false,
        modal: true,
		autoOpen: false,
		draggable: false,
    	resizable: false,
		position: { my: "center", at: "center", of: window },
		open: function() {
			$(this).parent().css({
				position: "fixed",
				top: "50%",
				left: "50%",
				transform: "translate(-50%, -50%)",
				maxWidth: "90%",
				minWidth: "300px",
			});
	
			$(".ui-dialog-titlebar-close").html("&#10005;").css({
				fontSize: "20px", 
				color: "#fff", 
				backgroundColor: "#f44336",
				padding: "5px", 
				borderRadius: "50%",
			});
	
			$(".ui-dialog-content").css({
				padding: "20px",
				color: "#333",
				fontFamily: "Arial, sans-serif"
			});
		},
		close: function() {
			$(this).find(".ui-dialog-content").html("");
		},
        width: 400
    });

	$(".cadence-info").click(function() {
        $("#cadence-dialog").dialog("open");
    });
    $("#gear-ratio-info").click(function() {
        $("#gear-ratio-dialog").dialog("open");
    });
    $("#skid-patches-info").click(function() {
        $("#skid-patches-dialog").dialog("open");
    });
    $("#gear-inches-info").click(function() {
        $("#gear-inches-dialog").dialog("open");
    });

	$("#results-overlay").dialog({
		width: 600,
		height: 600,
		modal: true,
		autoOpen: false,
		draggable: false,
    	resizable: false,
		position: { my: "center", at: "center", of: window },
		open: function() {
			$(this).parent().css({
				position: "fixed",
				top: "50%",
				left: "50%",
				transform: "translate(-50%, -50%)",
				maxWidth: "90%",
				minWidth: "300px",
			});
	
			$(".ui-dialog-titlebar-close").html("&#10005;").css({
				fontSize: "20px", 
				color: "#fff", 
				backgroundColor: "#f44336",
				padding: "5px", 
				borderRadius: "50%",
			});
	
			$(".ui-dialog-content").css({
				padding: "20px",
				color: "#333",
				fontFamily: "Arial, sans-serif"
			});
		},
		close: function() {
			$(this).find(".ui-dialog-content").html("");
		}
	});
    $("#results-overlay").dialog("close");

    $("#close-dialog").click(function() {
        $("#results-overlay").dialog("close");
    });

    $("#about-dialog").dialog({
        modal: true,
        autoOpen: false,
		draggable: false,
    	resizable: false,
		position: { my: "center", at: "center", of: window },
        width: 400,
        open: function() {
			$(this).parent().css({
				position: "fixed",
				top: "50%",
				left: "50%",
				transform: "translate(-50%, -50%)",
				maxWidth: "90%",
				minWidth: "300px",
			});

			$(".ui-dialog-titlebar-close").html("&#10005;").css({
				fontSize: "20px",
				color: "#fff",
				backgroundColor: "#f44336",
				padding: "5px",
				borderRadius: "50%",
			});

			$(".ui-dialog-content").css({
				padding: "20px",
				color: "#333",
				fontFamily: "Arial, sans-serif"
			});
		}
    });

    $("#about-btn").click(function() {
        $("#about-dialog").dialog("open");
    });

	function updateFileList() {
        fileList.empty();
        if (dataTransfer.files.length) {
            $.each(dataTransfer.files, function (index, file) {
                const fileItem = $(`<div class="file-object">${file.name} <span class="remove-file" data-index="${index}">✖</span></div>`);
                fileList.append(fileItem);
            });
        } else {
            fileList.append('<div>No files selected.</div>');
        }
    }

    fileInput.on('change', function () {
        const files = Array.from(fileInput.prop('files'));
        files.forEach(file => dataTransfer.items.add(file));
        fileInput.prop('files', dataTransfer.files);
        updateFileList();
    });

    $('#drop-area')
        .on('dragover', function (e) {
            e.preventDefault();
            $(this).addClass('drag-over');
        })
        .on('dragleave', function () {
            $(this).removeClass('drag-over');
        })
        .on('drop', function (e) {
            e.preventDefault();
            $(this).removeClass('drag-over');
            const droppedFiles = Array.from(e.originalEvent.dataTransfer.files);
            droppedFiles.forEach(file => dataTransfer.items.add(file));
            fileInput.prop('files', dataTransfer.files);
            updateFileList();
        });

    fileList.on('click', '.remove-file', function () {
        const index = $(this).data('index');
        dataTransfer.items.remove(index);
        fileInput.prop('files', dataTransfer.files);
        updateFileList();
    });

    updateFileList();

	$('#submit').on('click', function() {
		const formData = new FormData();
		const files = $('#files').prop('files');
//		const stravaLinks = $('#stravaLinks').val().trim();

		if (files.length === 0 && stravaLinks.length === 0) {
			alert('Please add GPX data to upload.');
			return;
		}

        $('#loading-overlay').fadeIn();
		$.each(files, function(index, file) {
			formData.append('files', file);
		});
//		if (stravaLinks) {
//            formData.append('links', JSON.stringify(stravaLinks.split('\n')));
//        }
		formData.append('wheel_circumference', $('#tire').val());
		formData.append('lang', $('#language-selector').val());
		$.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $('#loading-overlay').fadeOut();
                $("#results-overlay").dialog("open");
                updateResultsChart(response.data);
                $("#gear-ratio-explanation").text(response.explanation || "");
                $("#recommended-gear-ratio").text((response.optimal_gear_ratio[0]/response.optimal_gear_ratio[1]).toFixed(2));
                $('#chainring').val(response.optimal_gear_ratio[0]);
                $('#sprocket').val(response.optimal_gear_ratio[1]);
                calculate();
            },
            error: function(xhr, status, error) {
                if (xhr.status === 504) {
                    alert('The server timed out while processing your request. Please try uploading fewer files at once.');
                } else {
                    alert('Error uploading files: ' + error);
                }
                $('#loading-overlay').fadeOut();
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

function findGCD(a,b) { return ( b == 0 ) ? a : findGCD(b, a%b); }

function calculate() {
	let chainringT = parseInt($('#chainring').val());
	let sprocketT = parseInt($('#sprocket').val());
	drawConnectedGears(chainringT, sprocketT);
	let unit = $("input[name='unit']:checked").val();
	const ratio = Math.round(chainringT/sprocketT*100)/100;
	const tire = Number($('#tire').val());
	const tire_inches = tire / (Math.PI * 25.4);

	$('#ratio').html(ratio);
	$('#gear-inches').html(Math.ceil(ratio * tire_inches));
	$('#skid-patches').html(sprocketT/findGCD(chainringT, sprocketT));

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

	const cadenceStep = 10;
	const minCadence = 30;
	const maxCadence = 140;

	$('#speeds-table-body').empty();
	let rowsHtml = '';
	for (let cadence = minCadence; cadence <= maxCadence; cadence += cadenceStep * 2) {
		const speed1 = (cadence * development / 1000) * 60;
		const speed2 = ((cadence + cadenceStep) * development / 1000) * 60;

		const speed1Display = unit === "m" ? speed1.toFixed(2) : (speed1 * 0.621371).toFixed(2);
		const speed2Display = unit === "m" ? speed2.toFixed(2) : (speed2 * 0.621371).toFixed(2);

		const isInHighlightRange1 = cadence >= 70 && cadence <= 100;
		const isInHighlightRange2 = (cadence + cadenceStep) >= 70 && (cadence + cadenceStep) <= 100;
	
		const highlightClass1 = isInHighlightRange1 ? 'table-highlight' : '';
		const highlightClass2 = isInHighlightRange2 ? 'table-highlight' : '';
	
		rowsHtml += `
			<tr>
				<td class="${highlightClass1}">${cadence}</td>
				<td class="${highlightClass1}">${speed1Display}</td>
				<td class="${highlightClass2}">${cadence + cadenceStep}</td>
				<td class="${highlightClass2}">${speed2Display}</td>
			</tr>
		`;
	}
	$('#speeds-table-body').append(rowsHtml);

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

	const allCombinations = generateGearCombinations(28, 100, 11, 28);

	const filteredCombinations = allCombinations.filter(({ ratio }) => {
		return Math.abs(ratio - currentRatio) <= tolerance;
	});

	let row = $("<tr></tr>");
	filteredCombinations.forEach(({ ring, sprocket, ratio }, index) => {
		const cell = $(`<td title="${ratio}" onclick="changeGearRatio(${ring}, ${sprocket}, ${ratio})">${ring}×${sprocket}</td>`);
		row.append(cell);

		if ((index + 1) % (window.innerWidth > 768 ? 8 : 6) === 0) {
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
	$.getJSON('static/locales/' + lang + '.json', (translations_res) => {
		translations = translations_res;
		$('[data-translate]').each(function() {
			var key = $(this).data('translate');
			$(this).text(translations[key]);
		});
		calculate();
	});
}

function updateResultsChart(data) {
    const labels = [translations["cadence"], translations["heart-rate"], translations["estimated-power"], translations["speed"], translations["surface-quality"], translations["elevation-gain"]];
    const dataValues = [
        normalizeValue(data.avg_cadence, 0, 140),
        normalizeValue(data.avg_heart_rate, 40, 200),
        normalizeValue(data.avg_power, 0, data.avg_power > 500 ? data.avg_power : 500),
        normalizeValue(data.avg_speed, 0, data.avg_speed_threshold),
        normalizeValue(data.avg_surface, 0, 1),
        normalizeValue(data.elevation_gain, 0, data.elevation_threshold)
    ];
	const filteredLabels = labels.filter((_, index) => dataValues[index] !== 0);
	const filteredData = dataValues.filter(value => value !== 0);
    if (resultsChart) {
        resultsChart.data.labels = filteredLabels;
        resultsChart.data.datasets[0].data = filteredData;
        resultsChart.update();
    } else {
        const ctx = document.getElementById("resultsChart").getContext("2d");
        resultsChart = new Chart(ctx, {
            type: "radar",
            data: {
                labels: filteredLabels,
                datasets: [{
                    label: translations["route-metrics"],
                    data: filteredData,
                    backgroundColor: "rgba(54, 162, 235, 0.2)",
                    borderColor: "rgba(54, 162, 235, 1)",
                    borderWidth: 1,
					pointRadius: 0
                }]
            },
            responsive: true,
            maintainAspectRatio: true,
			options: { 
				scales: {
					r: {
                        min: 0,
                        max: 1,
					  ticks:{
						display: false
					  }
					}
				  },
				scale: {
					ticks: {
						display: false,
                        beginAtZero: true
					},
                    grid: {
                        display: false
                    },
                    angleLines: {
                        display: false
                    },
                    pointLabels: {
                        display: false
                    }
				}
			}
        });
    }
}

function normalizeValue(value, min, max) {
    let returnValue = value ? (value - min) / (max - min) : 0;
	if (returnValue > 1) returnValue = 1;
    return value > 1 ? returnValue : value;
}

function drawConnectedGears(chainringTeeth, sprocketTeeth) {
    const canvas = document.getElementById('gearCanvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const toothSize = 0.87;
    const chainringRadius = chainringTeeth * toothSize;
    const sprocketRadius = sprocketTeeth * toothSize;

    const chainringX = 2 * canvas.width / 3;
    const chainringY = canvas.height / 2;
    const sprocketX = canvas.width / 3;
    const sprocketY = canvas.height / 2;

    function drawGear(x, y, radius, teeth, color) {
        ctx.save();
        ctx.translate(x, y);
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;

        ctx.beginPath();
        ctx.arc(0, 0, radius, 0, 2 * Math.PI);
        ctx.stroke();

        const toothAngle = (2 * Math.PI) / teeth;
        for (let i = 0; i < teeth; i++) {
            const angle = i * toothAngle;
            const innerX = Math.cos(angle) * radius;
            const innerY = Math.sin(angle) * radius;
            const outerX = Math.cos(angle) * (radius + 5);
            const outerY = Math.sin(angle) * (radius + 5);

            ctx.beginPath();
            ctx.moveTo(innerX, innerY);
            ctx.lineTo(outerX, outerY);
            ctx.stroke();
        }

        ctx.beginPath();
        ctx.arc(0, 0, radius / 4, 0, 2 * Math.PI);
        ctx.stroke();

        ctx.restore();
    }

    function drawChain() {
        ctx.save();
        ctx.strokeStyle = '#888';
        ctx.lineWidth = 3;

        const midX = (chainringX + sprocketX) / 2;
        const midY = (chainringY + sprocketY) / 2;

        const chainPathRadius = Math.hypot(chainringX - sprocketX, chainringY - sprocketY) / 2;
        const curveOffset = 35;

        ctx.beginPath();
        ctx.moveTo(chainringX, chainringY - chainringRadius);
        ctx.quadraticCurveTo(midX, midY - curveOffset, sprocketX, sprocketY - sprocketRadius);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(chainringX, chainringY + chainringRadius);
        ctx.quadraticCurveTo(midX, midY + curveOffset, sprocketX, sprocketY + sprocketRadius);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(sprocketX, sprocketY, sprocketRadius, Math.PI / 2, 3 * Math.PI / 2);
        ctx.strokeStyle = '#888';
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(chainringX, chainringY, chainringRadius, -Math.PI / 2, Math.PI / 2);
        ctx.strokeStyle = '#888';
        ctx.stroke();

        ctx.restore();
    }

    drawGear(chainringX, chainringY, chainringRadius, chainringTeeth, '#C0C0C0');
    drawGear(sprocketX, sprocketY, sprocketRadius, sprocketTeeth, '#D4AF37');

    drawChain();
}


