var metricsApiUrl = "http://localhost:5002";
var modelNames = [];
var emotionCounts = {};
var emotionTrends = {};
var emotionTrendsAggregate = {};
var aggregateDatapointNo = 99; // Number of datapoints to aggregate for trend line
var emotions = ["Afraid", "Angry", "Disgusted", "Happy", "Neutral", "Sad", "Surprised"];
//  If emotion is positive, we assume the AI was correct
var positiveEmotions = ["Happy"]
//  If emotion is negative, we assume the AI was incorrect
var negativeEmotions = ["Angry", "Disgusted", "Sad"]
//  If emotion is neutral, we cannot make an assumption on whether the AI was correct or not
var neutralEmotions = ["Afraid", "Neutral", "Surprised"]
var dragOptions = {
    animationDuration: 1000
};
$( document ).ready(function() {
    let bodyHtml = "<table id=\"metricsTable\">";
    $.get(metricsApiUrl+"/getMetrics", function(resp) {
        let count = 0;
        let emotionScores = [];
        let aggregateTimestamp = new Date(JSON.parse(resp.body[0])["timestamp"]*1000);
        resp.body.forEach(function(element) {
            element = JSON.parse(element);
            if (!(modelNames.includes(element["modelName"]))) {
                modelNames.push(element["modelName"]);
                emotionCounts[element["modelName"]] = {"counts": [0,0,0,0,0,0,0]};
                emotionTrends[element["modelName"]] = []
                emotionTrendsAggregate[element["modelName"]] = [{"x": new Date(element["timestamp"]*1000), "y": 0.5}] // Set first value to 50% as initial (random chance) accuracy will be 50%
            }
            // Update metric tallies
            let emotionScore;
            emotionCounts[element["modelName"]]["counts"][emotions.indexOf(element["emotion"])] += 1;
            if (positiveEmotions.includes(element["emotion"])) {
                emotionTrends[element["modelName"]].push({"x": new Date(element["timestamp"]*1000), "y": 1});
                emotionScore = 1;
            }
            if (negativeEmotions.includes(element["emotion"])) {
                emotionTrends[element["modelName"]].push({"x": new Date(element["timestamp"]*1000), "y": 0});
                emotionScore = 0;
            }
            if (neutralEmotions.includes(element["emotion"])) {
                emotionTrends[element["modelName"]].push({"x": new Date(element["timestamp"]*1000), "y": 0.5});
                emotionScore = 0.5;
            }
            emotionScores.push(emotionScore);
            if (count % aggregateDatapointNo == 0 && count != 0) {
                var sum = 0;
                for( var i = 0; i < emotionScores.length; i++ ){
                    sum += parseInt(emotionScores[i], 10 );
                }
                emotionScoreAverage = sum/emotionScores.length;
                emotionTrendsAggregate[element["modelName"]].push({"x": new Date(element["timestamp"]*1000), "y": emotionScoreAverage});
                emotionScores = [];
                aggregateTimestamp = new Date(element["timestamp"]*1000);
            }
            count += 1;
        });
        console.log(emotionCounts)
        console.log(emotionTrends)
        console.log(emotionTrendsAggregate)
        // Construct elements
        modelNames.forEach(function(model) {
            bodyHtml += `<tr><td>${model}</td>`;
            // Emotion breakdown chart
            bodyHtml += `<td><canvas id=\"crt${model}ebd\"></canvas></td>`;
            // Accuracy
            bodyHtml += `<td><canvas id=\"crt${model}acc\"></canvas></td>`;
            bodyHtml += "</tr>";
        });
        bodyHtml += "</table>";
        if (resp.body.length == 0) {
            bodyHtml="No data found.";
        }
        $("#content").html(bodyHtml);
        // Render charts
        modelNames.forEach(function(model) {
            // Emotion breakdown
            var ctx = document.getElementById(`crt${model}ebd`);
            var crtEmotionBreakdown = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: emotions,
                    datasets: [{
                        label: `Emotion breakdown for ${model}`,
                        data: emotionCounts[model]["counts"],
                        backgroundColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(200, 0, 100, 1)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(200, 0, 100, 1)'
                        ],
                        borderWidth: 1
                    }]
                }
            });
            var cty = document.getElementById(`crt${model}acc`)
            var crtAccuracyTrend = new Chart(cty, {
                type: 'line',
                data: {
                    datasets: [{
                    //     label: "Positivity",
                    //     borderColor: "green",
                    //     backgroundColor: "rgba(0,255,0,0.2)",
                    //     data: emotionTrends[model],
                    //     order: 2
                    // }, {
                        label: "Aggregate Positivity",
                        borderColor: "rgba(255,0,0,0.4)",
                        backgroundColor: "rgba(255,0,0,0.2)",
                        data: emotionTrendsAggregate[model],
                        type: "line"
                    }]
                },
                options: {
                    // responsive: true,
                    scales: {
                        xAxes: [{
                            type: 'time'
                        }],
                        yAxes: [{
                            display: true,
                            ticks: {
                                beginAtZero: true,
                                max: 1
                            }
                        }]
                    },
                    plugins: {
                        zoom: {
                            zoom: {
                                enabled: true,
                                drag: dragOptions,
                                mode: 'x',
                                speed: 0.05
                            }
                        }
                    }
                }
            });
        });
    });
});

function updateTrendAggregationLevel(level){
    $("#aggLevel").html(level);
}