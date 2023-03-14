"use strict";
!function() {
    function formatParams() {
        let url = document.getElementById("url").value;
        if (!url) return "";
        let params = {
          url: url
        };

        document.getElementById("query-params").value.split(/\r?\n/).forEach((line) => {
            line = line.replace(/^\s+|\s+$/g, '');
            if (line) {
                let parts = line.split("=");
                if (parts.length === 2) {
                    params[parts[0]] = parts[1];
                } else if (parts.length === 1) {
                    params[parts[0]] = null;
                }
            }
        });

        return "?" + Object
            .keys(params)
            .map((key) => {
                if (params[key] === null) return key;
                return key+"="+encodeURIComponent(params[key]);
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
                    try {
                        let response = JSON.parse(xhr.responseText);
                        // Print array of errors as li elements
                        errors.innerHTML = response.err.map((err) => {
                            return "<li>" + err + "</li>";
                        });
                    } catch(err) {
                        errors.innerHTML = "<li>Unknown error. See the server log for more details.</li>";
                    }
                    errors.style.display = "block";
                }
                scrapeIt.innerHTML = "Scrape it!";
                scrapeIt.removeAttribute("aria-busy");
            }
        };
        scrapeIt.innerHTML = "Please wait…";
        scrapeIt.setAttribute("aria-busy", "true");
    });

    var url = document.getElementById("url");
    var queryParams = document.getElementById("query-params");

    // watch for changes in the query params and update the snippet
    function updateSnippet() {
        let params = formatParams();

        // create a snippet
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

        // save the query params to local storage
        localStorage.setItem('url', url.value);
        localStorage.setItem('queryParams', queryParams.value);
    }

    // code below is executed when the page loads...

    // load the query params and the url from local storage
    url.value = localStorage.getItem('url') || "";
    queryParams.value = localStorage.getItem('queryParams') || "";

    // add event listeners to the url and query params fields to update the snippet and save to local storage
    url.addEventListener("input", updateSnippet);
    queryParams.addEventListener("input", updateSnippet);

    // then open the query params details if there are query params in local storage already (i.e. the user has already used the scrapper)
    if (queryParams.value) {
        document.getElementById("query-params-details").setAttribute("open", "");
    }
}();
