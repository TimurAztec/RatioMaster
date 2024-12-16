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