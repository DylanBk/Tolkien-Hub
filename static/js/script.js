// --- SWITCH SIGNUP/LOGIN FORMS ---

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


// DRAG AND DROP FILE UPLOADER/PREVIEW ---

const drop_area = document.getElementById("file-drop-area");
const file_input = document.getElementById("file-input");
const upload_button = document.getElementById("file-upload-btn");
let selected_file = null;

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

drop_area.addEventListener('dragover', preventDefaults);
drop_area.addEventListener('dragenter', preventDefaults);
drop_area.addEventListener('dragleave', preventDefaults);
drop_area.addEventListener('drop', handleDrop);

drop_area.addEventListener('dragover', () => {
    drop_area.style.backgroundColor = "#d3d3d3";
});

drop_area.addEventListener('dragleave', () => {
    drop_area.style.backgroundColor = "#fff";
});

upload_button.addEventListener('mouseover', () => {
    if (selected_file) {
        upload_button.style.cursor = "pointer";
        upload_button.style.background = "#2563eb";
    } else {
        upload_button.style.cursor = "not-allowed"
    }
});

upload_button.addEventListener('mouseout', () => {
    upload_button.style.background = "#3b82f6";
})

upload_button.addEventListener('click', async () => {
    console.log("upload button clicked")
    if (selected_file) {
        await uploadFile(selected_file);
        location.reload()
    } else {
        alert("No file selected.");
    }
});

function handleDrop(e) {
    preventDefaults(e);
    const files = e.dataTransfer.files;

    if (files.length > 1) {
        alert("Please upload only one file.");
        return;
    }

    if (files.length === 1) {
        selected_file = files[0];
        handleFiles(files);
        upload_button.disabled = false;
    }
}

function handleFiles(files) {
    const preview_container = document.getElementById("preview-container");
    preview_container.innerHTML = '';

    const file = files[0];

    if (isValidFileType(file)) {
        const reader = new FileReader();
        reader.readAsDataURL(file);

        reader.onloadend = (e) => {
            const preview = document.createElement('img');
            preview.src = e.target.result;
            preview.classList.add('preview-image');
            const preview_container = document.getElementById("preview-container");
            preview_container.appendChild(preview);
        };
    } else {
        console.error(`Invalid file type: ${file.type}`);
    }
}

function isValidFileType(file) {
    const allowed_types = ['image/jpeg', 'image/png', 'image/gif'];
    return allowed_types.includes(file.type);
}

async function uploadFile(file) {
    let username = document.getElementById("user-username").textContent.trim();
    const url = `/profile/${username}/edit/change-pfp`;
    const form_data = new FormData();

    form_data.append('file', file);

    try {
            const response = await fetch(url, {
                method: 'POST',
                body: form_data
            })

            console.log(response)

            if (!response.ok) {
                throw new Error(`Failed to upload file. Server responded with status:${response.status}`);
            };

            const data = await response.json();

            if (data.success) {
                console.log("success");
                const user_pfp = document.getElementById("user-pfp");
                user_pfp.src = data.newUserPFP;
            };
    } catch (error) {
        console.error(`Error: ${error}`);
        alert(error.message);
        };
};


// --- SHOW CHANGE PFP FORM ---

const change_pfp_btn = document.getElementById("edit-pfp-btn");
const cancel_change_pfp_btn = document.getElementById("cancel-change-pfp-btn");
const change_pfp_form_container = document.getElementById("change-pfp-form-container");

change_pfp_btn.addEventListener('click', () => {
    console.log("button pressed")
    change_pfp_form_container.style.display = "block";
});

cancel_change_pfp_btn.addEventListener('click', () => {
    console.log("cancel pressed")
    change_pfp_form_container.style.display = "none";
    document.getElementById("preview-container").innerHTML = ''
    selected_file = null;
});


