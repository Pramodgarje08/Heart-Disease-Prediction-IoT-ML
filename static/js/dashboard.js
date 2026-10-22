let selectedPatient = "";
let monitorTimer = null;

const canvas = document.getElementById("ecgCanvas");
const ctx = canvas.getContext("2d");

const hrCanvas = document.getElementById("hrChart");
const hrCtx = hrCanvas.getContext("2d");

const spo2Canvas = document.getElementById("spo2Chart");
const spo2Ctx = spo2Canvas.getContext("2d");


function showPage(id) {
    document
        .querySelectorAll(".page")
        .forEach(page => {
            page.classList.remove("active");
        });

    document
        .getElementById(id)
        .classList.add("active");

    if (id === "patients") {
        loadPatients();
    }
}


async function loadPatients() {
    try {
        const response = await fetch("/api/patients");
        const data = await response.json();

        if (!Array.isArray(data)) {
            return;
        }

        document
            .getElementById("totalPatients")
            .textContent = data.length;

        document
            .getElementById("patientRows")
            .innerHTML = data.map(p => `
                <tr>
                    <td>${p.patient_id || "-"}</td>
                    <td>${p.name || "-"}</td>
                    <td>${p.age || "-"}</td>
                    <td>${p.gender || "-"}</td>
                </tr>
            `).join("");

    } catch (error) {
        console.error(
            "Patient loading error:",
            error
        );
    }
}


async function registerPatient() {

    const data = {
        patient_id:
            document
                .getElementById("pid")
                .value
                .trim(),

        name:
            document
                .getElementById("pname")
                .value
                .trim(),

        age:
            document
                .getElementById("page")
                .value,

        gender:
            document
                .getElementById("pgender")
                .value
    };


    if (
        !data.patient_id ||
        !data.name ||
        !data.age ||
        !data.gender
    ) {
        alert(
            "Please fill all patient details."
        );
        return;
    }


    try {

        const response = await fetch(
            "/api/patients",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(data)
            }
        );


        const result =
            await response.json();

        const msg =
            document.getElementById("regmsg");


        if (result.status === "success") {

            msg.textContent =
                "Patient registered successfully: " +
                result.patient_id;

            msg.style.color = "#16803c";


            document
                .getElementById("pid")
                .value = "";

            document
                .getElementById("pname")
                .value = "";

            document
                .getElementById("page")
                .value = "";


            loadPatients();

        } else {

            msg.textContent =
                result.message ||
                "Registration failed";

            msg.style.color = "#d62828";
        }

    } catch (error) {

        console.error(error);

        document
            .getElementById("regmsg")
            .textContent =
            "Server connection error";
    }
}


function startMonitoring() {

    selectedPatient =
        document
            .getElementById("monitorPatient")
            .value
            .trim();


    if (!selectedPatient) {

        alert("Enter Patient ID");

        return;
    }


    document
        .getElementById("selectedPatient")
        .textContent =
        selectedPatient;


    if (monitorTimer) {
        clearInterval(monitorTimer);
    }


    updateMonitoring();


    monitorTimer =
        setInterval(
            updateMonitoring,
            1000
        );
}


function stopMonitoring() {

    if (monitorTimer) {

        clearInterval(
            monitorTimer
        );

        monitorTimer = null;
    }
}


async function updateMonitoring() {

    if (!selectedPatient) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/history/" +
                encodeURIComponent(
                    selectedPatient
                )
            );


        const data =
            await response.json();


        if (
            !Array.isArray(data) ||
            data.length === 0
        ) {
            return;
        }


        const latest = data[0];


        const hr =
            Number(
                latest.heart_rate || 0
            );

        const spo2 =
            Number(
                latest.spo2 || 0
            );

        const ecg =
            Number(
                latest.ecg || 0
            );


        document
            .getElementById("monitorHR")
            .textContent =
            hr.toFixed(0) + " BPM";


        document
            .getElementById("monitorSpO2")
            .textContent =
            spo2.toFixed(0) + " %";


        document
            .getElementById("monitorECG")
            .textContent =
            ecg.toFixed(0);


        let risk =
            latest.risk_level || "-";

        let prediction =
            latest.prediction || "-";


        /* Sensor validation */

        if (
            hr <= 0 ||
            spo2 <= 0 ||
            ecg <= 0
        ) {

            risk =
                "Data Insufficient";

            prediction =
                "Insufficient Sensor Data";
        }


        setRisk(
            "monitorRisk",
            risk
        );

        setRisk(
            "dashboardRisk",
            risk
        );


        document
            .getElementById(
                "monitorPrediction"
            )
            .textContent =
            prediction;


        document
            .getElementById(
                "monitorConfidence"
            )
            .textContent =
            "Confidence: " +
            (
                Number(
                    latest.confidence || 0
                ) * 100
            ).toFixed(1) + "%";


        document
            .getElementById(
                "monitorModel"
            )
            .textContent =
            "Model: " +
            (
                latest.model_name ||
                "Random Forest"
            );


        /* Dashboard */

        document
            .getElementById(
                "dashboardHR"
            )
            .textContent =
            hr.toFixed(0) + " BPM";


        document
            .getElementById(
                "dashboardSpO2"
            )
            .textContent =
            spo2.toFixed(0) + " %";


        document
            .getElementById(
                "dashboardECG"
            )
            .textContent =
            ecg.toFixed(0);


        document
            .getElementById(
                "dashboardPrediction"
            )
            .textContent =
            prediction;


        document
            .getElementById(
                "dashboardConfidence"
            )
            .textContent =
            (
                Number(
                    latest.confidence || 0
                ) * 100
            ).toFixed(1) + "%";


        /* ECG */

        drawECG(
            data
                .slice(0, 100)
                .reverse()
                .map(
                    x =>
                        Number(
                            x.ecg || 0
                        )
                )
        );


        /* HR */

        drawHR(
            data
                .slice(0, 30)
                .reverse()
                .map(
                    x =>
                        Number(
                            x.heart_rate || 0
                        )
                )
        );


        /* SpO2 */

        drawSpO2(
            data
                .slice(0, 30)
                .reverse()
                .map(
                    x =>
                        Number(
                            x.spo2 || 0
                        )
                )
        );


    } catch (error) {

        console.error(
            "Monitoring error:",
            error
        );
    }
}


function setRisk(id, risk) {

    const element =
        document.getElementById(id);


    element.textContent = risk;


    element.classList.remove(
        "risk-high",
        "risk-medium",
        "risk-low"
    );


    const value =
        String(risk).toLowerCase();


    if (value === "high") {

        element.classList.add(
            "risk-high"
        );

    } else if (value === "medium") {

        element.classList.add(
            "risk-medium"
        );

    } else if (value === "low") {

        element.classList.add(
            "risk-low"
        );
    }
}


/* ECG GRAPH */

function drawECG(values) {

    const width =
        canvas.clientWidth * 2;

    const height =
        canvas.clientHeight * 2;


    canvas.width = width;
    canvas.height = height;


    ctx.clearRect(
        0,
        0,
        width,
        height
    );


    if (values.length < 2) {
        return;
    }


    const min =
        Math.min(...values);

    const max =
        Math.max(...values);

    const range =
        max - min || 1;


    ctx.fillStyle =
        "#101820";

    ctx.fillRect(
        0,
        0,
        width,
        height
    );


    /* Grid */

    ctx.strokeStyle =
        "#26333d";

    ctx.lineWidth = 1;


    const grid = 40;


    for (
        let x = 0;
        x < width;
        x += grid
    ) {

        ctx.beginPath();

        ctx.moveTo(x, 0);

        ctx.lineTo(
            x,
            height
        );

        ctx.stroke();
    }


    for (
        let y = 0;
        y < height;
        y += grid
    ) {

        ctx.beginPath();

        ctx.moveTo(
            0,
            y
        );

        ctx.lineTo(
            width,
            y
        );

        ctx.stroke();
    }


    /* Center line */

    ctx.beginPath();

    ctx.strokeStyle =
        "#40505c";

    ctx.lineWidth = 1;

    ctx.moveTo(
        0,
        height / 2
    );

    ctx.lineTo(
        width,
        height / 2
    );

    ctx.stroke();


    /* Wave */

    ctx.beginPath();

    ctx.strokeStyle =
        "#39ff14";

    ctx.lineWidth = 3;

    ctx.shadowColor =
        "#39ff14";

    ctx.shadowBlur = 6;


    values.forEach(
        (value, index) => {

            const x =
                index *
                (
                    width /
                    (values.length - 1)
                );


            const y =
                height -
                (
                    (
                        value - min
                    ) / range
                ) *
                (
                    height * 0.8
                ) -
                height * 0.1;


            if (index === 0) {

                ctx.moveTo(
                    x,
                    y
                );

            } else {

                ctx.lineTo(
                    x,
                    y
                );
            }
        }
    );


    ctx.stroke();

    ctx.shadowBlur = 0;
}


/* HR GRAPH */

function drawHR(values) {

    drawVitalGraph(
        hrCanvas,
        hrCtx,
        values,
        "BPM"
    );
}


/* SpO2 GRAPH */

function drawSpO2(values) {

    drawVitalGraph(
        spo2Canvas,
        spo2Ctx,
        values,
        "%"
    );
}


/* HR / SpO2 COMMON GRAPH */

function drawVitalGraph(
    canvasElement,
    context,
    values,
    unit
) {

    const width =
        canvasElement.clientWidth * 2;

    const height =
        canvasElement.clientHeight * 2;


    canvasElement.width = width;
    canvasElement.height = height;


    context.clearRect(
        0,
        0,
        width,
        height
    );


    if (values.length < 2) {
        return;
    }


    let min =
        Math.min(...values);

    let max =
        Math.max(...values);


    if (unit === "BPM") {

        min =
            Math.min(
                min,
                40
            );

        max =
            Math.max(
                max,
                140
            );

    } else {

        min =
            Math.min(
                min,
                85
            );

        max =
            Math.max(
                max,
                100
            );
    }


    const range =
        max - min || 1;


    /* Background */

    context.fillStyle =
        "#101820";

    context.fillRect(
        0,
        0,
        width,
        height
    );


    /* Grid */

    context.strokeStyle =
        "#26333d";

    context.lineWidth = 1;


    const grid = 40;


    for (
        let x = 0;
        x < width;
        x += grid
    ) {

        context.beginPath();

        context.moveTo(x, 0);

        context.lineTo(
            x,
            height
        );

        context.stroke();
    }


    for (
        let y = 0;
        y < height;
        y += grid
    ) {

        context.beginPath();

        context.moveTo(
            0,
            y
        );

        context.lineTo(
            width,
            y
        );

        context.stroke();
    }


    /* Line */

    context.beginPath();

    context.strokeStyle =
        "#39ff14";

    context.lineWidth = 3;

    context.shadowColor =
        "#39ff14";

    context.shadowBlur = 5;


    values.forEach(
        (value, index) => {

            const x =
                index *
                (
                    width /
                    (values.length - 1)
                );


            const y =
                height -
                (
                    (
                        value - min
                    ) / range
                ) *
                (
                    height * 0.8
                ) -
                height * 0.1;


            if (index === 0) {

                context.moveTo(
                    x,
                    y
                );

            } else {

                context.lineTo(
                    x,
                    y
                );
            }
        }
    );


    context.stroke();

    context.shadowBlur = 0;
}


/* HISTORY */

async function loadHistory() {

    const id =
        document
            .getElementById(
                "historyPatient"
            )
            .value
            .trim();


    if (!id) {

        alert(
            "Enter Patient ID"
        );

        return;
    }


    try {

        const response =
            await fetch(
                "/api/history/" +
                encodeURIComponent(id)
            );


        const data =
            await response.json();


        if (!Array.isArray(data)) {

            alert(
                data.message ||
                "Patient not found"
            );

            return;
        }


        document
            .getElementById(
                "historyRows"
            )
            .innerHTML =
            data.map(
                x => `

                <tr>

                    <td>
                        ${x.timestamp || "-"}
                    </td>

                    <td>
                        ${x.age_at_test || "-"}
                    </td>

                    <td>
                        ${Number(
                            x.heart_rate || 0
                        ).toFixed(0)}
                    </td>

                    <td>
                        ${Number(
                            x.spo2 || 0
                        ).toFixed(0)}%
                    </td>

                    <td>
                        ${x.ecg || "-"}
                    </td>

                    <td class="risk">
                        ${x.risk_level || "-"}
                    </td>

                    <td>
                        ${x.prediction || "-"}
                    </td>

                </tr>

            `
            ).join("");


    } catch (error) {

        console.error(
            "History error:",
            error
        );

        alert(
            "Unable to load history"
        );
    }
}


/* PDF */

function generateReport() {

    const id =
        document
            .getElementById(
                "historyPatient"
            )
            .value
            .trim();


    if (!id) {

        alert(
            "Enter Patient ID"
        );

        return;
    }


    window.open(
        "/api/report/" +
        encodeURIComponent(id),
        "_blank"
    );
}


/* Initial Load */

loadPatients();

