/*
=========================================
SATARK v2.0
Dashboard JavaScript
=========================================
*/


// =========================================
// ANALOG CLOCK
// =========================================

const clock = document.getElementById("analogClock");
const ctx = clock.getContext("2d");

const radius = clock.width / 2;

ctx.translate(radius, radius);


function drawClock() {

    ctx.clearRect(
        -radius,
        -radius,
        clock.width,
        clock.height
    );

    drawClockFace();
    drawClockNumbers();
    drawClockHands();

    const now = new Date();

    document.getElementById("digitalTime").innerText =
        now.toLocaleTimeString();
}


function drawClockFace() {

    ctx.beginPath();

    ctx.arc(
        0,
        0,
        radius * 0.90,
        0,
        2 * Math.PI
    );

    ctx.fillStyle = "#101f30";
    ctx.fill();

    ctx.strokeStyle = "#35e89a";
    ctx.lineWidth = 4;
    ctx.stroke();


    // Center point

    ctx.beginPath();

    ctx.arc(
        0,
        0,
        5,
        0,
        2 * Math.PI
    );

    ctx.fillStyle = "#35e89a";
    ctx.fill();
}


function drawClockNumbers() {

    ctx.font =
        radius * 0.14 + "px Arial";

    ctx.textBaseline = "middle";
    ctx.textAlign = "center";

    ctx.fillStyle = "#ffffff";

    for (let num = 1; num <= 12; num++) {

        const angle =
            num * Math.PI / 6;

        ctx.rotate(angle);

        ctx.translate(
            0,
            -radius * 0.72
        );

        ctx.rotate(-angle);

        ctx.fillText(
            num.toString(),
            0,
            0
        );

        ctx.rotate(angle);

        ctx.translate(
            0,
            radius * 0.72
        );

        ctx.rotate(-angle);
    }
}


function drawClockHands() {

    const now = new Date();

    let hour = now.getHours();
    let minute = now.getMinutes();
    let second = now.getSeconds();


    hour = hour % 12;

    hour =
        hour * Math.PI / 6 +
        minute * Math.PI / (6 * 60) +
        second * Math.PI / (360 * 60);


    drawHand(
        hour,
        radius * 0.45,
        6,
        "#ffffff"
    );


    minute =
        minute * Math.PI / 30 +
        second * Math.PI / (30 * 60);


    drawHand(
        minute,
        radius * 0.65,
        4,
        "#35e89a"
    );


    second =
        second * Math.PI / 30;


    drawHand(
        second,
        radius * 0.75,
        2,
        "#ff4040"
    );
}


function drawHand(
    position,
    length,
    width,
    color
) {

    ctx.beginPath();

    ctx.lineWidth = width;
    ctx.lineCap = "round";

    ctx.strokeStyle = color;

    ctx.moveTo(0, 0);

    ctx.rotate(position);

    ctx.lineTo(
        0,
        -length
    );

    ctx.stroke();

    ctx.rotate(-position);
}


// Update clock every 500 ms

setInterval(
    drawClock,
    500
);

drawClock();


// =========================================
// EVENT LOG
// =========================================

let lastEvent = "";


function addEvent(message) {

    if (!message) {
        return;
    }

    if (message === lastEvent) {
        return;
    }

    lastEvent = message;

    const log =
        document.getElementById(
            "eventLog"
        );

    const entry =
        document.createElement(
            "div"
        );

    entry.className =
        "log-entry";

    const time =
        new Date().toLocaleTimeString();

    entry.innerText =
        time + " • " + message;

    log.prepend(entry);


    // Keep maximum 20 events

    while (
        log.children.length > 20
    ) {

        log.removeChild(
            log.lastChild
        );
    }
}
// =========================================
// LIVE SATARK STATUS
// =========================================

async function updateStatus() {

    try {

        const response = await fetch(
            "/status",
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(
                "Status API unavailable"
            );
        }

        const data = await response.json();

        const ai = data.ai;
        const sensors = data.sensors;
        const alert = data.alert;


        // =================================
        // DRIVER STATUS
        // =================================

        document.getElementById(
            "driverStatus"
        ).innerText = ai.status;


        document.getElementById(
            "fps"
        ).innerText = ai.fps;


        // =================================
        // EYE STATUS
        // =================================

        if (!ai.driver_present) {

            document.getElementById(
                "eyeStatus"
            ).innerText = "--";

        }

        else if (ai.eyes_detected) {

            document.getElementById(
                "eyeStatus"
            ).innerText = "OPEN";

        }

        else {

            document.getElementById(
                "eyeStatus"
            ).innerText = "CLOSED";

        }


        // =================================
        // DHT11
        // =================================

        document.getElementById(
            "temperature"
        ).innerText =
            sensors.temperature === null
                ? "--"
                : Number(
                    sensors.temperature
                ).toFixed(1);


        document.getElementById(
            "humidity"
        ).innerText =
            sensors.humidity === null
                ? "--"
                : Number(
                    sensors.humidity
                ).toFixed(1);


        // =================================
        // FOUR ULTRASONIC SENSORS
        // =================================

        document.getElementById(
            "frontDistance"
        ).innerText =
            sensors.front_display;

        document.getElementById(
            "backDistance"
        ).innerText =
            sensors.back_display;

        document.getElementById(
            "leftDistance"
        ).innerText =
            sensors.left_display;

        document.getElementById(
            "rightDistance"
        ).innerText =
            sensors.right_display;


        // =================================
        // ALCOHOL SENSOR
        // =================================

        const alcoholIndicator =
            document.getElementById(
                "alcoholIndicator"
            );

        const alcoholStatus =
            document.getElementById(
                "alcoholStatus"
            );


        if (sensors.alcohol_detected) {

            alcoholStatus.innerText =
                "ALCOHOL DETECTED";

            alcoholIndicator.className =
                "status-indicator danger";

        }

        else {

            alcoholStatus.innerText =
                "NO ALCOHOL DETECTED";

            alcoholIndicator.className =
                "status-indicator safe";

        }


        // =================================
        // SENSOR HARDWARE STATUS
        // =================================

        const hardwareIndicator =
            document.getElementById(
                "hardwareIndicator"
            );

        const hardwareStatus =
            document.getElementById(
                "hardwareStatus"
            );


        if (sensors.hardware_connected) {

            hardwareStatus.innerText =
                "SENSORS ONLINE";

            hardwareIndicator.className =
                "status-indicator safe";

        }

        else {

            hardwareStatus.innerText =
                "WAITING FOR SENSORS";

            hardwareIndicator.className =
                "status-indicator warning";

        }
        // =================================
        // DRIVER SAFETY INDICATOR
        // =================================

        const driverIndicator =
            document.getElementById(
                "driverIndicator"
            );

        const safetyStatus =
            document.getElementById(
                "safetyStatus"
            );


        if (ai.drowsy) {

            safetyStatus.innerText =
                "DROWSINESS DETECTED";

            driverIndicator.className =
                "status-indicator danger";

        }

        else if (ai.head_down) {

            safetyStatus.innerText =
                "HEAD DOWN DETECTED";

            driverIndicator.className =
                "status-indicator danger";

        }

        else if (!ai.driver_present) {

            safetyStatus.innerText =
                "SEARCHING DRIVER";

            driverIndicator.className =
                "status-indicator warning";

        }

        else {

            safetyStatus.innerText =
                "DRIVER NORMAL";

            driverIndicator.className =
                "status-indicator safe";

        }


        // =================================
        // MASTER ALERT
        // =================================

        let alertActive = false;
        let alertMessage = "";


        if (ai.drowsy) {

            alertActive = true;
            alertMessage =
                "DROWSINESS DETECTED";

        }

        else if (ai.head_down) {

            alertActive = true;
            alertMessage =
                "HEAD DOWN DETECTED";

        }

        else if (sensors.alcohol_detected) {

            alertActive = true;
            alertMessage =
                "ALCOHOL DETECTED";

        }

        else if (sensors.obstacle) {

            alertActive = true;
            alertMessage =
                "OBSTACLE TOO CLOSE";

        }

        else if (
            sensors.temperature_warning
        ) {

            alertActive = true;
            alertMessage =
                "HIGH CABIN TEMPERATURE";

        }

        else if (alert.active) {

            alertActive = true;
            alertMessage =
                alert.type;

        }


        // =================================
        // FLASHING ALERT UI
        // =================================

        const alertPanel =
            document.getElementById(
                "alertPanel"
            );

        const cameraAlert =
            document.getElementById(
                "cameraAlert"
            );

        const alertText =
            document.getElementById(
                "alertText"
            );


        if (alertActive) {

            alertPanel.classList.add(
                "active"
            );

            cameraAlert.classList.add(
                "active"
            );

            alertText.innerText =
                alertMessage;

            cameraAlert.innerText =
                "🚨 " +
                alertMessage +
                " 🚨";

            addEvent(alertMessage);

        }

        else {

            alertPanel.classList.remove(
                "active"
            );

            cameraAlert.classList.remove(
                "active"
            );

            addEvent(ai.status);

        }


        // =================================
        // SYSTEM ONLINE
        // =================================

        const systemStatus =
            document.getElementById(
                "systemStatus"
            );

        systemStatus.innerText =
            "● SYSTEM ONLINE";

        systemStatus.className =
            "online";

    }

    catch (error) {

        console.error(
            "SATARK status error:",
            error
        );

        const systemStatus =
            document.getElementById(
                "systemStatus"
            );

        systemStatus.innerText =
            "● SYSTEM OFFLINE";

        systemStatus.style.color =
            "#ff4040";
    }
}


// =========================================
// AUTO UPDATE
// =========================================

// Update dashboard every 500 ms

setInterval(
    updateStatus,
    500
);

// Initial update

updateStatus();
