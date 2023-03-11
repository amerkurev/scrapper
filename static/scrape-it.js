"use strict";
!function() {
    function formatParams() {
        var url = document.getElementById("url").value;
        if (!url) return "";
        var params = {
          url: url
        };
        return "?" + Object
            .keys(params)
            .map((key) => {
                return key+"="+encodeURIComponent(params[key])
            })
            .join("&");
    };

    var scrapeIt = document.getElementById("scrape-it");
    scrapeIt.addEventListener("click", (e) => {
        e.preventDefault();
        var errors = document.getElementById("errors");
        var params = formatParams();
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/parse" + params, true);
        xhr.send();
        xhr.onreadystatechange = (e) => {
            if (xhr.readyState == 4) { // DONE: The operation is complete.
                if (xhr.status == 200) {
                    var response = JSON.parse(xhr.responseText);
                    window.location.href = "/view/" + response.id;
                } else {
                    // Handle error
                    var response = JSON.parse(xhr.responseText);
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

    // watch for changes in the query params
    var url = document.getElementById("url");
    url.addEventListener("input", (e) => {
        var params = formatParams();
        var snippet = document.getElementById("snippet");
        var snippetLink = document.getElementById("snippetLink");
        var snippetLabel = document.getElementById("snippetLabel");
        if (params === "") {
          snippet.style.display = "none";
        } else {
          var hostname = window.location.protocol + "//" + window.location.host;
          snippetLink.innerHTML = hostname + params;
          snippetLink.setAttribute("href", "/parse" + params);
          snippetLabel.innerHTML = "Request URL:"
          snippet.style.display = "block";
        }
    });
}();
