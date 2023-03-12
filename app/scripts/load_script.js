var loadErr = [];

async () => {
    return await new Promise((resolve) => {
        try {
            let s = document.createElement("script");
            s.onload = resolve;
            s.onerror = () => {
                loadErr.push("The script could not be loaded: %(src)s");
                resolve();
            };
            s.setAttribute("src", "%(src)s");
            document.head.appendChild(s);
        } catch(err) {
            loadErr.push("load_script.js: " + err.toString());
            resolve();
        }
    });
}
