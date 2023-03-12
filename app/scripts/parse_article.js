
() => {
    try {
        if (loadErr.length > 0) {
            return { err: loadErr };  // The Readability couldn't be loaded (see load_script.js for details)
        }
        try {
            // remove elements that are not visible
            var elements = document.body.getElementsByTagName("*");
            for (var i = 0; i < elements.length; i++) {
                var style = window.getComputedStyle(elements[i]);
                if (style.display === "none" ||
                    style.visibility === "hidden" ||
                    style.opacity === "0" ||
                    style.opacity === "0.0") {
                    elements[i].parentNode.removeChild(elements[i]);
                }
            }
            // parse the article with Mozilla's Readability.js
            return new Readability(document).parse();
        } catch(err) {
            return { err: ["Readability couldn't parse the document: " + err.toString()] };
        }
    } catch(err) {
        return { err: ["parse_article.js: " + err.toString()] };
    }
}
