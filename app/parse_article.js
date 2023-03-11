
() => {
    try {
        if (loadErr.length > 0) {
            return { err: loadErr };  // The Readability couldn't be loaded (see load_script.js for details)
        }
        try {
            return new Readability(document).parse();
        } catch(err) {
            return { err: ["Readability couldn't parse the document: " + err.toString()] };
        }
    } catch(err) {
        return { err: ["parse_article.js: " + err.toString()] };
    }
}
