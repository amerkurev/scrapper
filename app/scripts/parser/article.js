
() => {
    function findComments(el) {
        let arr = [];
        for (let i = 0; i < el.childNodes.length; i++) {
            let node = el.childNodes[i];
            // 8 is the Node.COMMENT_NODE constant
            // https://developer.mozilla.org/en-US/docs/Web/API/Node/nodeType
            if(node.nodeType === 8) {
                arr.push(node);
            } else {
                // recursively search for comments in child nodes
                arr.push.apply(arr, findComments(node));
            }
        }
        return arr;
    };

    try {
        // mark elements that are not visible
        let elements = document.body.getElementsByTagName("*");
        for (let i = 0; i < elements.length; i++) {
            let style = window.getComputedStyle(elements[i]);
            if (style.display === "none" ||
                style.visibility === "hidden" ||
                style.opacity === "0" ||
                style.opacity === "0.0") {
                elements[i].classList.add("scrapper-hidden");
            }
        }
        // remove invisible elements
        document.querySelectorAll(".scrapper-hidden").forEach(el => el.remove());

        // find and remove comments
        findComments(document.body).forEach(el => el.remove());

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
