const options = document.querySelectorAll(".option");


// =======================================
// SERVER ADDRESS
// =======================================

const SERVER_URL = (
    new URLSearchParams(window.location.search).get("backend") ||
    window.EYE_GAZE_BACKEND_URL ||
    "http://192.168.1.39:5000"
).replace(/\/+$/, "");


// =======================================
// DWELL TIME SETTINGS
// =======================================

const DWELL_TIME = 2000; // 2 seconds

let currentGazeOption = "";
let gazeStartTime = 0;
let selectedOption = "";


// =======================================
// REQUEST STATUS
// =======================================

let requestSent = false;


// Stores the option that was just acknowledged.
// This prevents the same option from being
// immediately selected again while the patient
// continues looking at it.

let acknowledgedOption = "";


// =======================================
// SPEECH FUNCTION
// =======================================

function speakMessage(optionName) {

    let message = "";


    if (optionName === "water") {

        message = "The patient needs water.";

    }

    else if (optionName === "toilet") {

        message =
            "The patient needs assistance to go to the toilet.";

    }

    else if (optionName === "pain") {

        message = "The patient is in pain.";

    }

    else if (optionName === "help") {

        message = "The patient needs help.";

    }


    if (message !== "") {

        window.speechSynthesis.cancel();

        const speech =
            new SpeechSynthesisUtterance(message);

        window.speechSynthesis.speak(
            speech
        );

    }

}


// =======================================
// SEND REQUEST TO CAREGIVER
// =======================================

async function sendRequest(optionName) {


    // -----------------------------------
    // PREVENT DUPLICATE REQUEST
    // -----------------------------------

    if (requestSent) {

        console.log(
            "Request already sent. Waiting for acknowledgement."
        );

        return;

    }


    try {

        const response =
            await fetch(

                SERVER_URL + "/request",

                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        option: optionName
                    })

                }

            );


        if (!response.ok) {

            throw new Error(
                "Request could not be sent"
            );

        }


        requestSent = true;


        console.log(
            "Request sent to caregiver:",
            optionName
        );


        updateConnectionStatus(true);

    }


    catch (error) {

        console.log(
            "Could not connect to caregiver:",
            error
        );


        updateConnectionStatus(false);

    }

}


// =======================================
// SELECT OPTION
// =======================================

function selectOption(optionName) {


    // -----------------------------------
    // INVALID OPTION
    // -----------------------------------

    if (
        !optionName ||
        optionName === "none"
    ) {

        return;

    }


    // -----------------------------------
    // REQUEST ALREADY WAITING
    // -----------------------------------

    if (requestSent) {

        console.log(
            "Waiting for caregiver acknowledgement."
        );

        return;

    }


    // -----------------------------------
    // SAME OPTION ALREADY SELECTED
    // -----------------------------------

    if (
        selectedOption === optionName
    ) {

        return;

    }


    // -----------------------------------
    // PREVENT IMMEDIATE RE-SELECTION
    // OF THE JUST-ACKNOWLEDGED OPTION
    // -----------------------------------

    if (
        acknowledgedOption === optionName
    ) {

        console.log(
            "Waiting for patient to look at another option."
        );

        return;

    }


    // -----------------------------------
    // SAVE SELECTION
    // -----------------------------------

    selectedOption =
        optionName;


    console.log(
        "SELECTED:",
        optionName
    );


    // -----------------------------------
    // SPEAK
    // -----------------------------------

    speakMessage(
        optionName
    );


    // -----------------------------------
    // SEND REQUEST
    // -----------------------------------

    sendRequest(
        optionName
    );

}


// =======================================
// CLICK FUNCTIONALITY
// =======================================

options.forEach((option) => {

    option.addEventListener(
        "click",
        () => {

            let optionName = "";


            if (
                option.classList.contains("water")
            ) {

                optionName = "water";

            }

            else if (
                option.classList.contains("toilet")
            ) {

                optionName = "toilet";

            }

            else if (
                option.classList.contains("pain")
            ) {

                optionName = "pain";

            }

            else if (
                option.classList.contains("help")
            ) {

                optionName = "help";

            }


            selectOption(
                optionName
            );

        }
    );

});


// =======================================
// EYE-GAZE TRACKING
// =======================================

async function checkGaze() {


    try {


        const response =
            await fetch(

                SERVER_URL +
                "/gaze",

                {
                    cache: "no-store"
                }

            );


        if (!response.ok) {

            throw new Error(
                "Gaze server unavailable"
            );

        }


        const data =
            await response.json();


        updateConnectionStatus(true);


        const lookingAt =
            (
                data.option || "NONE"
            ).toLowerCase();


        // ===================================
        // REMOVE ALL GLOW
        // ===================================

        options.forEach(
            (option) => {

                option.classList.remove(
                    "gaze-active"
                );

            }
        );


        // ===================================
        // ADD GLOW
        // ===================================

        const activeOption =
            document.querySelector(
                "." + lookingAt
            );


        if (activeOption) {

            activeOption.classList.add(
                "gaze-active"
            );

        }


        // ===================================
        // LOOKING AWAY / NONE
        // ===================================

        if (
            lookingAt === "none"
        ) {

            currentGazeOption = "";

            gazeStartTime = 0;

            selectedOption = "";

            updateProgress(0);

            return;

        }


        // ===================================
        // AFTER ACKNOWLEDGEMENT
        //
        // If patient is still looking at
        // the SAME option that was just
        // acknowledged, do nothing.
        //
        // If patient looks at a DIFFERENT
        // option, allow a new selection.
        // ===================================

        if (
            acknowledgedOption !== "" &&
            lookingAt === acknowledgedOption
        ) {

            currentGazeOption =
                lookingAt;

            gazeStartTime = 0;

            updateProgress(0);

            return;

        }


        // ===================================
        // PATIENT LOOKED AT A NEW OPTION
        // ===================================

        if (
            lookingAt !== currentGazeOption
        ) {

            currentGazeOption =
                lookingAt;

            gazeStartTime =
                Date.now();

            selectedOption = "";

            updateProgress(0);

        }


        // ===================================
        // CALCULATE DWELL TIME
        // ===================================

        const gazeDuration =
            Date.now() -
            gazeStartTime;


        const progress =
            Math.min(

                gazeDuration /
                DWELL_TIME,

                1

            );


        // ===================================
        // UPDATE PROGRESS
        // ===================================

        updateProgress(
            progress
        );


        // ===================================
        // SELECT AFTER 2 SECONDS
        // ===================================

        if (
            gazeDuration >=
            DWELL_TIME
        ) {

            // The patient has moved to a
            // different option, so the
            // previous acknowledgement
            // restriction can be removed.

            acknowledgedOption = "";


            selectOption(
                lookingAt
            );

        }

    }


    catch (error) {

        updateConnectionStatus(false);

        console.log(
            "Connection unavailable:",
            error
        );

    }

}


// =======================================
// CHECK CAREGIVER ACKNOWLEDGEMENT
// =======================================

async function checkAcknowledgement() {


    try {


        const response =
            await fetch(

                SERVER_URL +
                "/request",

                {
                    cache: "no-store"
                }

            );


        if (!response.ok) {

            throw new Error(
                "Server unavailable"
            );

        }


        const data =
            await response.json();


        // ===================================
        // CAREGIVER ACKNOWLEDGED
        // ===================================

        if (

            data.acknowledged === true &&

            requestSent === true

        ) {


            console.log(
                "Caregiver acknowledged request."
            );


            // Remember which option was
            // acknowledged

            acknowledgedOption =
                data.request;


            // Show confirmation

            showPatientConfirmation();


            // Request is no longer waiting

            requestSent = false;


            // Reset current selection

            selectedOption = "";


            // Reset progress

            updateProgress(0);


            // Reset dwell timer

            gazeStartTime = 0;

        }

    }


    catch (error) {

        console.log(
            "Could not check acknowledgement:",
            error
        );

    }

}


// =======================================
// PROGRESS INDICATOR
// =======================================

function updateProgress(progress) {


    const progressBar =
        document.getElementById(
            "gazeProgress"
        );


    const progressText =
        document.getElementById(
            "progressText"
        );


    if (!progressBar) {

        return;

    }


    // -----------------------------------
    // PROGRESS BAR
    // -----------------------------------

    progressBar.style.width =
        (
            progress * 100
        ) + "%";


    // -----------------------------------
    // PROGRESS TEXT
    // -----------------------------------

    if (progressText) {


        if (
            progress <= 0
        ) {

            progressText.innerText =
                "Look at an option";

        }


        else if (
            progress < 1
        ) {


            const seconds =
                (
                    progress * 2
                ).toFixed(1);


            progressText.innerText =

                "Hold your gaze... " +

                seconds +

                " / 2.0 seconds";

        }


        else {

            progressText.innerText =
                "✓ Option selected";

        }

    }

}


// =======================================
// PATIENT CONFIRMATION
// =======================================

function showPatientConfirmation() {


    const message =
        document.getElementById(
            "patientStatus"
        );


    if (!message) {

        return;

    }


    message.innerText =
        "✓ Caregiver has seen your request";


    message.style.color =
        "green";


    setTimeout(
        () => {

            message.innerText =
                "You can make another request.";

        },

        4000
    );

}


// =======================================
// CONNECTION STATUS
// =======================================

function updateConnectionStatus(
    connected
) {


    const status =
        document.getElementById(
            "connectionStatus"
        );


    if (!status) {

        return;

    }


    if (connected) {

        status.innerText =
            "🟢 System connected";

        status.style.color =
            "green";

    }

    else {

        status.innerText =
            "🔴 Connection unavailable";

        status.style.color =
            "red";

    }

}


// =======================================
// CHECK GAZE EVERY 150ms
// =======================================

setInterval(
    checkGaze,
    150
);


// =======================================
// CHECK ACKNOWLEDGEMENT EVERY 1 SECOND
// =======================================

setInterval(
    checkAcknowledgement,
    1000
);
