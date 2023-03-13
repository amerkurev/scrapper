"use strict";
!function() {
    function formatParams() {
        let url = document.getElementById("url").value;
        if (!url) return "";
        let params = {
          url: url
        };
        return "?" + Object
            .keys(params)
            .map((key) => {
                return key+"="+encodeURIComponent(params[key])
            })
            .join("&");
    };

    let scrapeIt = document.getElementById("scrape-it");
    scrapeIt.addEventListener("click", (e) => {
        e.preventDefault();
        let errors = document.getElementById("errors");
        let params = formatParams();
        let xhr = new XMLHttpRequest();
        xhr.open("GET", "/parse" + params, true);
        xhr.send();
        xhr.onreadystatechange = (e) => {
            if (xhr.readyState == 4) { // DONE: The operation is complete.
                if (xhr.status == 200) {
                    let response = JSON.parse(xhr.responseText);
                    window.location.href = "/view/" + response.id;
                } else {
                    // Handle error
                    let response = JSON.parse(xhr.responseText);
                    // Print array of errors as li elements
                    errors.innerHTML = response.err.map((err) => {
                        return "<li>" + err + "</li>";
                    });
                    errors.style.display = "block";
                }
                scrapeIt.innerHTML = "Scrape it!";
                scrapeIt.removeAttribute("aria-busy");
            }
        };
        scrapeIt.innerHTML = "Please wait…";
        scrapeIt.setAttribute("aria-busy", "true");
    });

    // watch for changes in the query params and update the snippet
    function updateSnippet() {
        let params = formatParams();
        let snippet = document.getElementById("snippet");
        let snippetLink = document.getElementById("snippetLink");
        let snippetLabel = document.getElementById("snippetLabel");
        if (params === "") {
            snippet.style.display = "none";
        } else {
            let hostname = window.location.protocol + "//" + window.location.host;
            snippetLink.innerHTML = hostname + "/parse" + params;
            snippetLink.setAttribute("href", "/parse" + params);
            snippetLabel.innerHTML = "Request URL:"
            snippet.style.display = "block";
        }
    }

    let url = document.getElementById("url");
    url.addEventListener("input", updateSnippet);
}();
