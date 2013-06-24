function cellPosition(cellele) {
    return { row: cellele.closest('tr').prop('rowIndex'), col: cellele.closest('td').prop('cellIndex') };
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
    return /^\d+$/.test(str);
}

function isBool(str) {
    if(str == '1' || str == '0') return true;
    
    var lowstr = str.toLowerCase();
    return (lowstr == 'true' || lowstr == 'false');
}

function isFloat(str) {
    return /^\d+(\.\d+)?$/.test(str);
    //return parseFloat(str) == str;
}

function isDateTime(str) {
    return /\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/.test(str);
}

function isTime(str) {
    return /\d{2}:\d{2}/.test(str);
}

function checkType(str, type) {
    str += ''; // convert to string
    switch(type) {
    case 'int': return isInt(str);
    case 'float': return isFloat(str);
    case 'datetime': return isDateTime(str);
    case 'bool': return isBool(str);
    case 'time': return isTime(str);
    }
    return true;
}

function checkData(data, attr) {
    if(!data) {
        if(attr.not_null || attr.primaryKey) return false;
        else return true;
    } else {
        return checkType(data, attr.type);
    }
}

function inRange(num, low, high) {
    return (num >= low && num <= high);
}

function deepCopy(obj) {
    if($.isPlainObject(obj)) {
        return $.extend(true, {}, obj);
    } else if($.isArray(obj)) {
        return $.extend(true, {}, {0:obj})[0];
    } else
        return obj;
}
function deepCmp(obj1, obj2) {
    if(typeof obj1 == 'number') obj1 += '';
    if(typeof obj2 == 'number') obj2 += '';
    var str1 = JSON.stringify(obj1), str2 = JSON.stringify(obj2);
    if(str1 == undefined) str1 = '';
    if(str2 == undefined) str2 = '';
    return str1.localeCompare(str2);
}

function arrayAt(arr, index) {
    for(var i = 0; i < index.length; i++) {
        arr = arr[index[i]];
        if(arr == undefined)
            return undefined;
    }
    return arr;
}
// for compatibility
/*function deepCopyArray(arr) {
    return $.extend(true, {}, {0:arr})[0];
}
*/