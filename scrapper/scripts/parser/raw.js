() => {
    try {
        return document.body.innerText;
    } catch(err) {
        return { err: ["Couldn't read the document: " + err.toString()] };
    }
}
