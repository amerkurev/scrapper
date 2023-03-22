
() => {
    function parseFontSize(s) {
        return parseInt(s.replace(/[px]/g, ''))
    };

    function parseRGB(s) {
        return s.replace(/[^\d,]/g, '').split(',').map((x) => parseInt(x));
    };

    function getCssSelector(el) {
        let path = [], parent;
        while (parent = el.parentNode) {
            path.unshift(el.tagName);
            el = parent;
        }
        return `${path.join(' > ')}`.toLowerCase();
    };

    try {
        links = [];
        num = 0;
        // remove elements that are not visible
        let elements = document.body.getElementsByTagName("*");
        for (let i = 0; i < elements.length; i++) {
            let style = window.getComputedStyle(elements[i]);
            if (style.display === "none" ||
                style.visibility === "hidden" ||
                style.opacity === "0" ||
                style.opacity === "0.0") {
                elements[i].parentNode.removeChild(elements[i]);
            } else if (elements[i].tagName === "A") {
                // extract links
                let text = elements[i].innerText.trim();
                let href = elements[i].getAttribute("href");
                if (text && href) {
                    let parentStyle = window.getComputedStyle(elements[i].parentNode);
                    let link = {
                        "num": num,
                        "cssSel": getCssSelector(elements[i]),
                        "text": text,
                        "length": text.length,
                        "href": href,
                        "color": parseRGB(style.color),  // e.g. "rgb(51, 51, 51)"
                        "fontSize": parseFontSize(style.fontSize),  // e.g. "12px"
                        "fontWeight": parseInt(style.fontWeight),  // e.g. "400"
                        "font": style.font,
                        "parentPadding": parentStyle.padding,
                        "parentMargin": parentStyle.margin,
                        "parentBackgroundColor": parentStyle.backgroundColor,
                    };
                    if (link.fontSize !== 0) {
                        links.push(link);
                    }
                }
                num += 1;
            }
        }
        return links;
    } catch(err) {
        return { err: [err.toString()] };
    }
}
