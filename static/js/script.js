const form_container = document.getElementById("form-container")
const signup_form_container = document.getElementById("signup-form-container");
const signup_form_switch = document.getElementById("signup-form-switch");
const signup_form = document.getElementById("signup-form");
const login_form_container = document.getElementById("login-form-container");
const login_form_switch = document.getElementById("login-form-switch");
const login_form = document.getElementById("login-form");
const form_container_left_block = document.getElementById("form-container-left-block");
const form_container_right_block = document.getElementById("form-container-right-block");

function switch_to_signup_form() {
    form_container.style.borderTopLeftRadius = "1.5rem";
    form_container.style.borderTopRightRadius = "0"
    login_form_container.style.visibility = "hidden";
    login_form.style.visibility = "hidden";
    login_form_switch.style.visibility = "visible";
    signup_form_container.style.visibility = "visible";
    signup_form.style.visibility = "visible";
    signup_form_switch.style.visibility = "hidden";
    form_container_left_block.style.visibility = "hidden";
    form_container_right_block.style.visibility = "visible"
};

function switch_to_login_form() {
    form_container.style.borderTopLeftRadius = "0"
    form_container.style.borderTopRightRadius = "1.5rem"
    signup_form_container.style.visibility = "hidden";
    signup_form.style.visibility = "hidden";
    signup_form_switch.style.visibility = "visible";
    login_form_container.style.visibility = "visible";
    login_form.style.visibility = "visible";
    login_form_switch.style.visibility = "hidden";
    form_container_left_block.style.visibility = "visible";
    form_container_right_block.style.visibility = "hidden"
}