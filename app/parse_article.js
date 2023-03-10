
() => {
    if (typeof Readability === 'undefined') {
        return { err: "The Readability library hasn't loaded correctly." };
    }
    try {
        return new Readability(document).parse();
    } catch(err) {
        return { err: "The Readability couldn't parse the document: " + err.toString() };
    }
}
