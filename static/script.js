import json from "https://ipinfo.io/json" with { type: "json" };
function roundCoordinates(inputStr) {
    function roundMatch(match) {
        let number = parseFloat(match);
        return number.toFixed(2);
    }

    let resultStr = inputStr.replace(/\d+\.\d+/g, roundMatch);
    resultStr = resultStr.replace(/(\.\d*?[1-9])0+$/, '$1');
    resultStr = resultStr.replace(/\.(?=\D|$)/, '');
    return resultStr;
}
export function getLoc(){
    console.log("Client IP:", json.loc);
    document.getElementById("location").value = roundCoordinates(json.loc);
}

