function checkOverflow(cell) {
    return (cell.prop('scrollWidth') > cell.innerWidth() || cell.text().indexOf('\n') >= 0)
}
function cellPosition(cell) {
    return { row: cell.closest('tr').prop('rowIndex'), col: cell.prop('cellIndex') };
}
function createArray(length) {
    var arr = new Array(length || 0),
    i = length;
    
    if (arguments.length > 1) {
        var args = Array.prototype.slice.call(arguments, 1);
        while(i--) arr[length - 1 - i] = createArray.apply(this, args);
    }
    return arr;
}
function textToHtml(text) {
    return text.replace(/\n/g, '<BR>');
}

function isInt(str) {
    return parseInt(str) == str;
    //return (str.length < 10 && /^[0-9]+$/.test(str));
}
function isFloat(str) {
    return parseFloat(str) == str;
}
function isDateTime(str) {
    return /\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/.test(str);
}
function deepCopyArray(arr) {
        return $.extend(true, {}, {0:arr})[0];
}