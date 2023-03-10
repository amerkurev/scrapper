
async () => {
    return await new Promise((resolve) => {
        try {
            let s = document.createElement("script");
            s.onload = resolve;
            s.onerror = resolve;
            s.setAttribute("src", "%(src)s");
            document.head.appendChild(s);
        } catch(err) {
            resolve();
        }
    });
}
