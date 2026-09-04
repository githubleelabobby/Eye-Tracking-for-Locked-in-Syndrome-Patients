const options = document.querySelectorAll(".option");

// ---------------------------------------
// DWELL TIME SETTINGS
// ---------------------------------------

let currentGazeOption = "";
let gazeStartTime = 0;
let selectedOption = "";

const DWELL_TIME = 2000; // 2 seconds


// ---------------------------------------
// SPEECH FUNCTION
// ---------------------------------------

function speakMessage(optionName) {

    let message = "";

    if (optionName === "water") {
        message = "The patient needs water.";
    }

    else if (optionName === "toilet") {
        message = "The patient needs assistance to go to the toilet.";
    }

    else if (optionName === "pain") {
        message = "The patient is in pain.";
    }

    else if (optionName === "help") {
        message = "The patient needs help.";
    }

    if (message !== "") {

        window.speechSynthesis.cancel();

        const speech = new SpeechSynthesisUtterance(message);

        window.speechSynthesis.speak(speech);

    }

}


// ---------------------------------------
// SEND REQUEST TO CAREGIVER
// ---------------------------------------

async function sendRequest(optionName) {

    try {

        await fetch(
            "http://127.0.0.1:5000/request",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    option: optionName
                })
            }
        );

        console.log(
            "Request sent to caregiver:",
            optionName
        );

    }

    catch (error) {

        console.log(
            "Could not send caregiver request"
        );

    }

}


// ---------------------------------------
// SELECT OPTION
// ---------------------------------------

function selectOption(optionName) {

    if (selectedOption === optionName) {
        return;
    }

    selectedOption = optionName;

    console.log(
        "SELECTED:",
        optionName
    );

    speakMessage(optionName);

    sendRequest(optionName);

}


// ---------------------------------------
// CLICK FUNCTIONALITY
// ---------------------------------------

options.forEach((option) => {

    option.addEventListener("click", () => {

        let optionName = "";

        if (option.classList.contains("water")) {
            optionName = "water";
        }

        else if (option.classList.contains("toilet")) {
            optionName = "toilet";
        }

        else if (option.classList.contains("pain")) {
            optionName = "pain";
        }

        else if (option.classList.contains("help")) {
            optionName = "help";
        }

        selectOption(optionName);

    });

});


// ---------------------------------------
// EYE GAZE TRACKING
// ---------------------------------------

async function checkGaze() {

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/gaze"
        );

        const data = await response.json();

        const lookingAt = data.option.toLowerCase();


        // Remove glow from all options

        options.forEach((option) => {

            option.classList.remove(
                "gaze-active"
            );

        });


        // Add glow to detected option

        const activeOption = document.querySelector(
            "." + lookingAt
        );

        if (activeOption) {

            activeOption.classList.add(
                "gaze-active"
            );

        }


        // ---------------------------------------
        // DWELL TIME LOGIC
        // ---------------------------------------

        if (lookingAt === "none") {

            currentGazeOption = "";
            gazeStartTime = 0;

            return;

        }


        // If gaze changed to a new option

        if (lookingAt !== currentGazeOption) {

            currentGazeOption = lookingAt;

            gazeStartTime = Date.now();

            // Allow a new selection

            selectedOption = "";

        }


        // Calculate how long user has
        // looked at this option

        const gazeDuration =
            Date.now() - gazeStartTime;


        // Select only after 2 seconds

        if (gazeDuration >= DWELL_TIME) {

            selectOption(lookingAt);

        }

    }

    catch (error) {

        console.log(
            "Eye tracking server not connected"
        );

    }

}


// ---------------------------------------
// CHECK GAZE CONTINUOUSLY
// ---------------------------------------

setInterval(
    checkGaze,
    150
);