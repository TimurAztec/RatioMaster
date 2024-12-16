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
	const g = 9.81;
    const rollingResistanceCoefficient = 0.004;

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
	let speedsRowsHtml = '';
	for (let cadence = minCadence; cadence <= maxCadence; cadence += cadenceStep * 2) {
		const speed1 = (cadence * development / 1000) * 60;
		const speed2 = ((cadence + cadenceStep) * development / 1000) * 60;

		const speed1Display = unit === "m" ? speed1.toFixed(2) : (speed1 * 0.621371).toFixed(2);
		const speed2Display = unit === "m" ? speed2.toFixed(2) : (speed2 * 0.621371).toFixed(2);

		const isInHighlightRange1 = cadence >= 70 && cadence <= 100;
		const isInHighlightRange2 = (cadence + cadenceStep) >= 70 && (cadence + cadenceStep) <= 100;
	
		const highlightClass1 = isInHighlightRange1 ? 'table-highlight' : '';
		const highlightClass2 = isInHighlightRange2 ? 'table-highlight' : '';
	
		speedsRowsHtml += `
			<tr>
				<td class="${highlightClass1}">${cadence}</td>
				<td class="${highlightClass1}">${speed1Display}</td>
				<td class="${highlightClass2}">${cadence + cadenceStep}</td>
				<td class="${highlightClass2}">${speed2Display}</td>
			</tr>
		`;
	}
	$('#speeds-table-body').append(speedsRowsHtml);

	const weight = ($("#toggle-weight").val() && $("#input-weight").val()) ? $("#input-weight").val() : 80;

	$('#powers-table-body').empty();
	let powersRowsHtml = '';
	for (let gradient = 5; gradient <= 20; gradient += 10) {
		const slope = gradient / 100;
		const rollingResistanceForce = rollingResistanceCoefficient * weight * g;
		const gravityForce = slope * weight * g;
		const totalForce = rollingResistanceForce + gravityForce;

		const speed = (minCadence * development) / 60;
		const power = totalForce * speed;

		powersRowsHtml += `
			<tr>
				<td>${gradient}%</td>
				<td>${Math.floor(power)} W</td>
				<td>${(gradient + 5)}%</td>
				<td>${Math.floor(totalForce * (speed + 0.5))} W</td>
			</tr>
		`;
	}
	$('#powers-table-body').append(powersRowsHtml);

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