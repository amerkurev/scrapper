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

    let selectRoute = document.getElementById("select-route");
    let scrapeIt = document.getElementById("scrape-it");
    scrapeIt.addEventListener("click", (e) => {
        e.preventDefault();
        let errors = document.getElementById("errors");
        let params = formatParams();
        let xhr = new XMLHttpRequest();
        xhr.open("GET", apiEndpoint + params, true);  // the apiEndpoint variable is defined in the index.html
        xhr.send();
        xhr.onreadystatechange = (e) => {
            if (xhr.readyState == 4) { // DONE: The operation is complete.
                if (xhr.status == 200) {
                    let response = JSON.parse(xhr.responseText);
                    window.location.href = "/view/" + response.id;
                } else {
                    // Handle error
                    try {
                        // pretty print the xhr.responseText
                        let json = JSON.parse(xhr.responseText);
                        errors.innerHTML = "<pre>An error occurred\n" + JSON.stringify(json, null, 2) + "</pre>";
                    } catch(err) {
                        errors.innerHTML = "<pre>An error occurred. See the server log for more details.</pre>";
                    }
                    errors.style.display = "block";
                }
                scrapeIt.innerHTML = "Scrape it!";
                scrapeIt.removeAttribute("aria-busy");
                selectRoute.style.visibility = "visible";
            }
        };
        scrapeIt.innerHTML = "Please wait…";
        scrapeIt.setAttribute("aria-busy", "true");
        selectRoute.style.visibility = "hidden";
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
            snippetLink.innerHTML = hostname + apiEndpoint + params;
            snippetLink.setAttribute("href", apiEndpoint + params);
            snippetLabel.innerHTML = "Request URL:"
            snippet.style.display = "block";
        }

        // save the query params to local storage
        localStorage.setItem("url", url.value);
        localStorage.setItem("queryParams", queryParams.value);
    }

    // code below is executed when the page loads...
    url.value = localStorage.getItem("url") || "";
    queryParams.value = localStorage.getItem("queryParams") || "";
    updateSnippet();

    // add event listeners to the url and query params fields to update the snippet and save to local storage
    url.addEventListener("input", updateSnippet);
    queryParams.addEventListener("input", updateSnippet);

    // then open the query params details if there are query params in local storage already (i.e. the user has already used the scrapper)
    if (queryParams.value) {
        document.getElementById("query-params-details").setAttribute("open", "");
    }
}();
