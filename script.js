/* =========================================================
   SAMPATTI-SETU
   COMPLETE SCRIPT
   ========================================================= */


/* =========================================================
   ELEMENTS
   ========================================================= */

const citizenTab = document.getElementById("citizenTab");
const policeTab = document.getElementById("policeTab");
const loginSwitch = document.querySelector(".login-switch");

const loginTitle = document.getElementById("loginTitle");
const loginDescription = document.getElementById("loginDescription");
const loginIcon = document.getElementById("loginIcon");

const mobileLabel = document.getElementById("mobileLabel");
const mobileDescription = document.getElementById("mobileDescription");

const policeIdBox = document.getElementById("policeIdBox");
const policeId = document.getElementById("policeId");

const mobile = document.getElementById("mobile");
const sendOtp = document.getElementById("sendOtp");

const otpStep = document.getElementById("otpStep");
const otpText = document.getElementById("otpText");

const captchaStep = document.getElementById("captchaStep");
const captchaText = document.getElementById("captchaText");
const captchaInput = document.getElementById("captchaInput");

const refreshCaptcha = document.getElementById("refreshCaptcha");
const verifyButton = document.getElementById("verifyButton");

const timer = document.getElementById("timer");
const status = document.getElementById("status");

const otpInputs = document.querySelectorAll(".otp");


/* =========================================================
   VARIABLES
   ========================================================= */

let loginType = "citizen";

let generatedOTP = "";

let generatedCaptcha = "";

let countdown = 45;

let timerInterval = null;

// Once OTP is sent, login type cannot be changed
let loginLocked = false;


/* =========================================================
   FIXED DEMO OTPs
   ========================================================= */

// DEMO ONLY
const CITIZEN_OTP = "304526";
const POLICE_OTP = "312509";


/* =========================================================
   CITIZEN LOGIN
   ========================================================= */

citizenTab.addEventListener("click", function () {

    // Don't allow switching after OTP
    if (loginLocked) {
        return;
    }

    loginType = "citizen";

    citizenTab.classList.add("active");
    policeTab.classList.remove("active");

    loginSwitch.classList.remove("police-active");

    loginTitle.textContent = "Citizen Login";

    loginDescription.textContent =
        "Access your account using your Aadhaar-linked mobile number";

    loginIcon.textContent = "♧";

    mobileLabel.textContent =
        "Aadhaar-linked Mobile Number";

    mobileDescription.textContent =
        "Enter the 10-digit mobile number linked with your Aadhaar";

    policeIdBox.classList.add("hidden");

    policeId.value = "";

    status.textContent = "";
});


/* =========================================================
   POLICE LOGIN
   ========================================================= */

policeTab.addEventListener("click", function () {

    // Don't allow switching after OTP
    if (loginLocked) {
        return;
    }

    loginType = "police";

    policeTab.classList.add("active");
    citizenTab.classList.remove("active");

    loginSwitch.classList.add("police-active");

    loginTitle.textContent = "Police Login";

    loginDescription.textContent =
        "Access your account using your Police ID and mobile number";

    loginIcon.textContent = "🛡";

    mobileLabel.textContent =
        "Registered Mobile Number";

    mobileDescription.textContent =
        "Enter the mobile number registered with your Police ID";

    policeIdBox.classList.remove("hidden");

    status.textContent = "";
});


/* =========================================================
   MOBILE NUMBER INPUT
   ========================================================= */

mobile.addEventListener("input", function () {

    // Only allow numbers
    this.value = this.value.replace(/\D/g, "");

    // Maximum 10 digits
    if (this.value.length > 10) {
        this.value = this.value.slice(0, 10);
    }
});


/* =========================================================
   POLICE ID INPUT
   ========================================================= */

policeId.addEventListener("input", function () {

    this.value = this.value.toUpperCase();

});


/* =========================================================
   SEND OTP
   ========================================================= */

sendOtp.addEventListener("click", function () {

    const mobileNumber = mobile.value.trim();


    /* -----------------------------------------
       Validate Police ID
       ----------------------------------------- */

    if (loginType === "police") {

        if (policeId.value.trim() === "") {

            status.textContent =
                "Please enter your Police ID.";

            status.style.color = "red";

            policeId.focus();

            return;
        }
    }


    /* -----------------------------------------
       Validate Mobile
       ----------------------------------------- */

    if (!/^\d{10}$/.test(mobileNumber)) {

        status.textContent =
            "Please enter a valid 10-digit mobile number.";

        status.style.color = "red";

        mobile.focus();

        return;
    }


    /* =================================================
       LOCK LOGIN TYPE
       ================================================= */

    loginLocked = true;

    citizenTab.disabled = true;
    policeTab.disabled = true;


    /* =================================================
       FIXED DEMO OTP
       ================================================= */

    if (loginType === "citizen") {

        generatedOTP = CITIZEN_OTP;

    } else {

        generatedOTP = POLICE_OTP;

    }


    // Show OTP in console for testing
    console.log("Demo OTP:", generatedOTP);


    /* -----------------------------------------
       Show OTP
       ----------------------------------------- */

    otpStep.classList.remove("hidden");

    otpText.textContent =
        "OTP sent to +91 ******" + mobileNumber.slice(-4);


    /* -----------------------------------------
       Generate CAPTCHA
       ----------------------------------------- */

    generateCaptcha();

    captchaStep.classList.remove("hidden");


    /* -----------------------------------------
       Status
       ----------------------------------------- */

    status.textContent =
        "OTP sent successfully.";

    status.style.color = "green";


    /* -----------------------------------------
       Disable Send OTP
       ----------------------------------------- */

    sendOtp.disabled = true;

    sendOtp.textContent =
        "OTP Sent";


    /* -----------------------------------------
       Start Timer
       ----------------------------------------- */

    startTimer();


    /* -----------------------------------------
       Clear Previous OTP
       ----------------------------------------- */

    otpInputs.forEach(function (input) {

        input.value = "";

    });


    /* -----------------------------------------
       Focus First OTP Box
       ----------------------------------------- */

    otpInputs[0].focus();

});


/* =========================================================
   OTP INPUT
   ========================================================= */

otpInputs.forEach((input, index) => {

    input.addEventListener("input", function () {

        // Only allow numbers
        this.value =
            this.value.replace(/\D/g, "");

        // Keep only one digit
        if (this.value.length > 1) {
            this.value = this.value.slice(0, 1);
        }


        // Move to next box
        if (
            this.value.length === 1 &&
            index < otpInputs.length - 1
        ) {

            otpInputs[index + 1].focus();

        }

    });


    /* -----------------------------------------
       Backspace
       ----------------------------------------- */

    input.addEventListener("keydown", function (event) {

        if (
            event.key === "Backspace" &&
            this.value === "" &&
            index > 0
        ) {

            otpInputs[index - 1].focus();

        }

    });

});


/* =========================================================
   OTP PASTE
   ========================================================= */

otpInputs[0].addEventListener("paste", function (event) {

    event.preventDefault();

    const pastedData =
        event.clipboardData
            .getData("text")
            .replace(/\D/g, "")
            .slice(0, 6);


    pastedData.split("").forEach((digit, index) => {

        if (otpInputs[index]) {

            otpInputs[index].value = digit;

        }

    });


    if (pastedData.length === 6) {

        otpInputs[5].focus();

    }

});


/* =========================================================
   TIMER
   ========================================================= */

function startTimer() {

    clearInterval(timerInterval);

    countdown = 45;

    updateTimer();


    timerInterval = setInterval(function () {

        countdown--;

        updateTimer();


        if (countdown <= 0) {

            clearInterval(timerInterval);

            timer.textContent =
                "You can resend OTP";

        }

    }, 1000);

}


function updateTimer() {

    const seconds =
        countdown.toString().padStart(2, "0");

    timer.textContent =
        "Resend OTP in 00:" + seconds;

}


/* =========================================================
   CAPTCHA GENERATOR
   ========================================================= */

function generateCaptcha() {

    const characters =
        "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

    generatedCaptcha = "";


    for (let i = 0; i < 5; i++) {

        generatedCaptcha +=
            characters.charAt(
                Math.floor(
                    Math.random() * characters.length
                )
            );

    }


    captchaText.textContent =
        generatedCaptcha;

    captchaInput.value = "";

}


/* =========================================================
   REFRESH CAPTCHA
   ========================================================= */

refreshCaptcha.addEventListener("click", function () {

    generateCaptcha();

    status.textContent = "";

});


/* =========================================================
   VERIFY LOGIN
   ========================================================= */

verifyButton.addEventListener("click", function () {


    /* -----------------------------------------
       Get OTP
       ----------------------------------------- */

    let enteredOTP = "";


    otpInputs.forEach(function (input) {

        enteredOTP += input.value;

    });


    /* -----------------------------------------
       Check OTP Length
       ----------------------------------------- */

    if (enteredOTP.length !== 6) {

        status.textContent =
            "Please enter the complete 6-digit OTP.";

        status.style.color = "red";

        return;

    }


    /* -----------------------------------------
       Check OTP
       ----------------------------------------- */

    if (enteredOTP !== generatedOTP) {

        status.textContent =
            "Invalid OTP. Please try again.";

        status.style.color = "red";

        return;

    }


    /* -----------------------------------------
       Check CAPTCHA
       ----------------------------------------- */

    if (
        captchaInput.value.trim().toUpperCase()
        !== generatedCaptcha
    ) {

        status.textContent =
            "Incorrect CAPTCHA. Please try again.";

        status.style.color = "red";

        generateCaptcha();

        return;

    }


    /* -----------------------------------------
       Login Successful
       ----------------------------------------- */

    status.textContent =
        loginType === "citizen"
            ? "Citizen login successful!"
            : "Police login successful!";

    status.style.color = "green";


    /* -----------------------------------------
       Disable Verify Button
       ----------------------------------------- */

    verifyButton.disabled = true;

    /* -----------------------------------------
       Save login role for the dashboard
       ----------------------------------------- */

    sessionStorage.setItem("sampattiSetuRole", loginType);
    sessionStorage.setItem("sampattiSetuPoliceId", policeId.value.trim());

    /* -----------------------------------------
       Redirect Police to Police Dashboard
       ----------------------------------------- */

    if (loginType === "police") {
        setTimeout(function () {
            window.location.href = "police.html";
        }, 700);
    }

    if (loginType === "citizen") {
        setTimeout(function() {
             window.location.href = "dashboard.html";
        },700)
    }

});


/* =========================================================
   INITIAL CAPTCHA
   ========================================================= */

generateCaptcha();