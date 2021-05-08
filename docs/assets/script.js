let trans = () => {
    document.documentElement.classList.add("transition");
    window.setTimeout(() => {
        document.documentElement.classList.remove("transition");
    }, 1000);
};


var checkbox = document.querySelector("input[name=mode]");
checkbox.addEventListener("change", function() {
    if (this.checked) {
        trans();
        document.documentElement.setAttribute("data-theme", "dartheme");
        document.cookie = "preference=dark";
        document.getElementById("1").src = 'assets/white.png';
        document.getElementById("2").src = 'assets/white.png';
    } else {
        trans();
        document.documentElement.setAttribute("data-theme", "lighttheme");
        document.cookie = "preference=light";
        document.getElementById("1").src = 'assets/black.png';
        document.getElementById("2").src = 'assets/black.png';
    }
});

let gDate = 0;

var vars = {};
var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(
    m,
    key,
    value
) {
    vars[key] = value;
});

gDate = vars.length - 0 + (vars.start - 0) - Date.now();

function convert(time) {
    if (!time) return "INVALID";

    var delta = Math.abs(time) / 1000;

    var days = Math.floor(delta / 86400);
    delta -= days * 86400;

    var hours = Math.floor(delta / 3600) % 24;
    delta -= hours * 3600;

    var minutes = Math.floor(delta / 60) % 60;
    delta -= minutes * 60;

    var seconds = delta % 60;
    seconds = Math.trunc(seconds);

    if (days > 0) {
        let day1 = days + ` day`;
        let hour1 = hours + ` hour`;
        if (days > 1) day1 += "s";
        if (hours > 1) hour1 += "s";
        if (hours === 0) return `${day1}`;
        return `${day1} and ${hour1}`;
    }
    if (hours > 0) {
        let hour1 = hours + ` hour`;
        let minute1 = minutes + ` minute`;
        if (hours > 1) hour1 += "s";
        if (minutes > 1) minute1 += "s";
        if (minutes === 0) return `${hour1}`;
        return `${hour1} and ${minute1}`;
    }
    if (minutes > 0) {
        let minute1 = minutes + ` minute`;
        let second1 = seconds + ` second`;
        if (minutes > 1) minute1 += "s";
        if (seconds > 1) second1 += "s";
        if (seconds === 0) return `${minute1}`;
        return `${minute1} and ${second1}`;
    }
    if (seconds > 0) {
        let second1 = seconds + ` second`;
        if (seconds > 1) second1 += "s";
        return `${second1}`;
    }
}

setInterval(function() {
    let getO = document.getElementById("timer");

    gDate = gDate - 1000;
    if (convert(gDate) === undefined) gDate = 0;
    if (gDate > 0) getO.innerHTML = convert(gDate) + " remaining";
    if (gDate <= 0) getO.innerHTML = "This giveaway has ended";
}, 1000);

let dt = new Date(vars.start - 0 + (vars.length - 0));
setInterval(() => {
    let current = new Date(Date.now());
    let getTs = document.getElementById("endDate");

    if (
        current.getDate() + 1 === dt.getDate() &&
        current.getMonth() === dt.getMonth() &&
        current.getFullYear() === dt.getFullYear()
    ) {
        getTs.innerHTML =
            "Ends: Tomorrow at " +
            ("0" + dt.getHours()).slice(-2) +
            ":" +
            ("0" + dt.getMinutes()).slice(-2);
        return;
    }
    if (gDate >= 86400000)
        getTs.innerHTML =
        "Ends At: " +
        ("0" + dt.getDate()).slice(-2) +
        "/" +
        ("0" + (dt.getMonth() + 1)).slice(-2) +
        "/" +
        dt.getFullYear() +
        ", " +
        ("0" + dt.getHours()).slice(-2) +
        ":" +
        ("0" + dt.getMinutes()).slice(-2);
    if (gDate < 86400000)
        getTs.innerHTML =
        "Ends: Today at " +
        ("0" + dt.getHours()).slice(-2) +
        ":" +
        ("0" + dt.getMinutes()).slice(-2);
    if (gDate <= 0)
        getTs.innerHTML =
        "Ended At: " +
        ("0" + dt.getDate()).slice(-2) +
        "/" +
        ("0" + (dt.getMonth() + 1)).slice(-2) +
        "/" +
        dt.getFullYear() +
        ", " +
        ("0" + dt.getHours()).slice(-2) +
        ":" +
        ("0" + dt.getMinutes()).slice(-2);
}, 1000);