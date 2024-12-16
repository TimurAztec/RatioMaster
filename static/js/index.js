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

	$(".additional-inputs-menu-header").click(function () {
        $(".additional-inputs-menu-body").slideToggle();
		const arrow = $(this).find("#additional-inputs-menu-toggle");
		arrow.text(arrow.text() === "▼" ? "▲" : "▼");
    });

	$("#toggle-weight").change(function () {
		$("#input-weight").prop("disabled", !this.checked);
		$(this).next("label").toggleClass("greyout", !this.checked);
	});

	$("#input-weight").change(function () {
		calculate();
	});

	$("#toggle-crank-length").change(function () {
		$("#input-crank-length").prop("disabled", !this.checked);
		$(this).next("label").toggleClass("greyout", !this.checked);
	});

	$("#toggle-ride-style").change(function () {
		$("#input-ride-style").prop("disabled", !this.checked);
		$(this).next("label").toggleClass("greyout", !this.checked);
	});

	$("#toggle-fixed-gear").change(function () {
		$(this).next("label").toggleClass("greyout", !this.checked);
	});

	$("#toggle-flat-pedals").change(function () {
		$(this).next("label").toggleClass("greyout", !this.checked);
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

		// Optional inputs
		if ($('#toggle-weight').is(':checked') && $('#input-weight').val().trim() !== '') {
			formData.append('weight', $('#input-weight').val().trim());
		}
		if ($('#toggle-crank-length').is(':checked') && $('#input-crank-length').val()) {
			formData.append('crank_length', $('#input-crank-length').val());
		}
		// if ($('#toggle-ride-style').is(':checked') && $('#input-ride-style').val()) {
		// 	formData.append('ride_style', $('#input-ride-style').val());
		// }
		if ($('#toggle-fixed-gear').is(':checked')) {
			formData.append('fixed_gear', true);
		}
		if ($('#toggle-flat-pedals').is(':checked')) {
			formData.append('flat_pedals', true);
		}

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

function normalizeValue(value, min, max) {
    let returnValue = value ? (value - min) / (max - min) : 0;
	if (returnValue > 1) returnValue = 1;
    return value > 1 ? returnValue : value;
}