
() => {
    try {
        // parse the article with Mozilla's Readability.js (https://videoinu.com/blog/firefox-reader-view-heuristics/)
        let documentClone = document.cloneNode(true);
        // https://github.com/mozilla/readability#api-reference
        let options = {
          maxElemsToParse: %(maxElemsToParse)d,
          nbTopCandidates: %(nbTopCandidates)d,
          charThreshold: %(charThreshold)d,
        }
        return new Readability(documentClone, options).parse();
    } catch(err) {
        return { err: "Readability couldn't parse the page: " + err.toString() };
    }
}
