
() => {
    function parseFontSize(s) {
        return parseInt(s.replace(/[px]/g, ''))
    };

    function getCssSelector(el) {
        let path = [], parent;
        while (parent = el.parentNode) {
            path.unshift(el.tagName);
            el = parent;
        }
        return `${path.join(' > ')}`.toLowerCase();
    };

    function replaceNbsps(str) {
        return str.replace(new RegExp(String.fromCharCode(160), "g"), " ");  // remove \xa0
    }

    function splitIntoWords(str) {
        return str.split(/[\r\n\s]+/).filter(s => s.length > 0);
    }

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
        // remove marked elements
        document.querySelectorAll(".scrapper-hidden").forEach(el => el.remove());

        // traverse the DOM tree and extract links
        let links = [];
        elements = document.body.getElementsByTagName("A");

        for (let i = 0; i < elements.length; i++) {
            let text = elements[i].innerText.trim();
            let href = elements[i].getAttribute("href");

            if (text && href && href !== "/" && href !== "#" && href !== "javascript:void(0)") {
                // get the computed style of the link and its parent
                let style = window.getComputedStyle(elements[i]);
                let parentStyle = window.getComputedStyle(elements[i].parentNode);

                let link = {
                    "pos": i,
                    "cssSel": getCssSelector(elements[i]),
                    "text": replaceNbsps(text),
                    "href": href,
                    "url": new URL(href, document.location).href,
                    "fontSize": parseFontSize(style.fontSize),  // e.g. "12px" -> 12
                    "fontWeight": parseInt(style.fontWeight),  // e.g. "400" -> 400
                    "color": style.color,  // e.g. "rgb(51, 51, 51)"
                    "font": style.font,
                    "parentPadding": parentStyle.padding,
                    "parentMargin": parentStyle.margin,
                    "parentBgColor": parentStyle.backgroundColor,
                };
                link["words"] = splitIntoWords(link.text);
                links.push(link);
            }
        }
        return links;
    } catch(err) {
        return { err: [err.toString()] };
    }
}
