"use strict";
!function() {
    function formatParams(params) {
        return "?" + Object
            .keys(params)
            .map((key) => {
                return key+"="+encodeURIComponent(params[key])
            })
            .join("&")
    };

    var scrapeIt = document.getElementById("scrape-it");
    scrapeIt.addEventListener("click", (e) => {
        e.preventDefault();
        var url = document.getElementById("url").value;
        if (!url) {
            return
        }
        var params = {url: url};
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/parse" + formatParams(params), true);
        xhr.send();
        xhr.onreadystatechange = (e) => {
            if (xhr.readyState == 4 && xhr.status == 200) {
                var response = JSON.parse(xhr.responseText);
                window.location.href = "/view/" + response.id;
            }
            // TODO: Handle errors
        };
        scrapeIt.innerHTML = "Please wait…";
        scrapeIt.setAttribute("aria-busy", "true");
    });
}();
