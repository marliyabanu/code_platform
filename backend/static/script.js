function validatePassword() {
    let p = document.getElementById("password").value;
    let error = document.getElementById("error");

    let regex = /[!@#$%^&*]/;

    if (p.length < 5) {
        error.innerHTML = "Min 5 chars";
        return false;
    }

    if (!regex.test(p)) {
        error.innerHTML = "Need special char";
        return false;
    }

    error.innerHTML = "";
    return true;
}

function toggleTheme() {
    document.body.classList.toggle("light");
}