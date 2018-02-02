/**
 * @return {string}
 */
function Get(webUrl) {
    var Httpreq = new XMLHttpRequest();
    Httpreq.open("GET", webUrl, false);
    Httpreq.send(null);
    return Httpreq.responseText;
}

function updateData() {
    var bikeData = JSON.parse(Get("./bikedata.json"));
    console.log("bike speed: " + bikeData.speed);
    setTimeout(updateData, 200);
}


//updateData();

function Point(x, y) {
    this.x = x;
    this.y = y;
}

var graphCanvas;
var graphContext;
var scrollback = 6000;
var fps = 50;
var data = [];
var dx;
var dt;
var y = 100;
var speedCanvas;
var speedContext;
var speed = 4;

function initializeDashboard() {
    graphCanvas = document.getElementById("graphCanvas");
    graphContext = graphCanvas.getContext("2d");
    speedCanvas = document.getElementById("speedCanvas");
    speedContext = speedCanvas.getContext("2d");
    dt = 1000 / fps;
    dx = (graphCanvas.width / dt) * (1000 / scrollback);
    console.log("graphElement.width="+graphCanvas.width);
    console.log("dt="+dt);
    console.log("dx="+dx);
    setInterval(getData, 50);
    setInterval(updateGraph, dt);
    setInterval(updateSpeedometer, dt);
}

function getData() {
    var sine = false;
    if (sine) {
        y = 250 + 100*Math.sin(Date.now() / 159.2);
    } else {
        var mult = 20;
        y = y + mult * (Math.random() - .5);
        if (y < 0)   y += mult;
        if (y > graphCanvas.height) y -= mult;
    }
    for (var i = 0; i < data.length; ++i) {
        data[i].x = data[i].x + dx;
    }
    data.push(new Point(0, y));
    if (data[0].x > graphCanvas.width) {
        data.splice(0, 1);
    }

    var dv = 0.3*(Math.random() - 0.5);
    if (speed + dv > 0.0 && speed + dv <= 15.0) {
        speed += dv;
    }
}

function updateGraph() {

    graphContext.clearRect(0, 0, graphCanvas.width, graphCanvas.height);
    graphContext.fillStyle = "red";
    graphContext.beginPath();
    for (var i = 0; i < data.length - 1; ++i) {
        graphContext.moveTo(data[i].x, data[i].y);
        graphContext.lineTo(data[i+1].x, data[i+1].y);
    }
    graphContext.stroke();
}

function updateSpeedometer() {
    var radius = Math.min(speedCanvas.height, speedCanvas.width) / 2 - 6;
    var needleLength = 0.70 * radius;
    var centerX = speedCanvas.width / 2;
    var centerY = speedCanvas.width / 2;
    speedContext.clearRect(0, 0, speedCanvas.width, speedCanvas.height);
    speedContext.beginPath();
    speedContext.lineWidth = 1;
    console.log("(" + centerX + ", " + centerY + "), r=" + radius)
    speedContext.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    speedContext.font = "12px Courier New";
    speedContext.fillStyle = "maroon";
    for (var s = 0.0; s <= 15.0; s += 1.0) {
        var markAngle = 1.25 * Math.PI - (1.5 * Math.PI * (s / 15.0));
        var markX0 = centerX + radius * Math.cos(markAngle);
        var markY0 = centerY - radius * Math.sin(markAngle);
        var markX1 = centerX + (0.9 * radius) * Math.cos(markAngle);
        var markY1 = centerY - (0.9 * radius) * Math.sin(markAngle);
        var markX2 = centerX + (0.83 * radius) * Math.cos(markAngle);
        var markY2 = centerY - (0.83 * radius) * Math.sin(markAngle);
        speedContext.moveTo(markX0, markY0);
        speedContext.lineTo(markX1, markY1);
        speedContext.fillText(s.toString(), markX2 - ((s < 10) ? 4 : 8), markY2 + 5);
    }
    var angle = 1.25 * Math.PI - (1.5 * Math.PI * (speed / 15.0));
    var needleX = centerX + needleLength * Math.cos(angle);
    var needleY = centerY - needleLength * Math.sin(angle);
    speedContext.stroke();
    speedContext.beginPath();
    var fontSize = Math.ceil(0.16 * radius);
    speedContext.font = fontSize.toString() + "px Courier New";
    speedContext.fillStyle = "gold";
    speedContext.fillText(
        speed.toLocaleString(undefined, {minimumIntegerDigits: 2, minimumFractionDigits: 2, maximumFractionDigits: 2}) + " m/s",
        centerX - (9.0 * 0.6 * fontSize) / 2,
        centerY + .7 * radius);
    speedContext.lineWidth = 3;
    speedContext.moveTo(centerX, centerY);
    speedContext.lineTo(needleX, needleY);
    speedContext.stroke();

}

//squareDraw();
//document.onload = squareDraw;
