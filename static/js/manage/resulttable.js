function ResultTable(tableid, schema, data) {
    var outer = this;
    this.$table = $('#' + tableid);
    this.schema = deepCopy(schema);
    this.buildSchema(this.schema);
    //this.$verbose = $('#resultVerbose');
    // callback
    this.defaultCallback = {
        cellDataFromEdit: function(cell) {
            return cell.find('input').val();
        },
        editLeaf: function(cell, obj) {
            if(cell.data('mode') == 'edit') return cell;
            
            cell.html('<input type="text" class="cell-content input" value="' + obj + '">');
            //cell.css('padding', 0);
            cell.find('input').focus().select();
            cell.data('mode', 'edit');
            return cell;
        },
        editNonLeaf: function(cell, obj) {
            return cell;
        },
        viewNonLeaf: function(cell, obj) {
            $.each(outer.cellChildren(cell), function(key, value) {
                outer.view(value, obj ? obj[key] : undefined);
            });
            return cell;
        },
        viewLeaf: function(cell, obj) {
            //if(cell.data('mode') == 'view') return cell;
            var attr = outer.attrAt(outer.cellIndex(cell));
            //cell.removeClass().addClass('cell text-cropped').css('padding', '2%');
            if(cell.attr('rtLevel') == 1) {
                cell.html(obj);
            } else {
                var prefix = attr.name + ': ';
                cell.data('view_prefix', prefix);
                cell.html(prefix + obj);
                //cell.append(obj);
            }
            cell.data('mode', 'view');
            return cell;
        },
        
        popover_cellDataFromEdit: function(pop) {
            return pop.find('textarea').val();
        },
        popover_edit: function(ele, pop) {
            if(pop.data('mode') == 'edit') return pop;
            pop.data('mode', 'edit');
            
            pop.find('.popover-content')
                .html('<div><textarea style="height:100px">_text</textarea></div> \
                    <div style="text-align:center;"><button class="btn btn-primary">保存</button> \
                    <button class="btn">放弃</button></div>'.replace('_text', outer.getCellCache(ele)));
            pop.find('textarea').focus().select();
            
            ele.popoverex('pin');
            // register button events
            var buttons = pop.find('button');
            var close = function() {
                buttons.each(function() {
                    $(this).off('click');
                });
                pop.data('mode', 'view');
                ele.popoverex('unpin');
                ele.popoverex('hide');
            };
            $(buttons[0]).click(function() {
                close(); // we must close first or popover information may be overwritten by modifyCell
                outer.modifyCell(ele, outer.callback(ele, 'popover_cellDataFromEdit')(pop));
            });
            $(buttons[1]).click(close);
            
            return pop;
        },
        popover_content: function() {
            // this = element that triggers callback
            return '<div style="word-wrap:break-word;">_text</div> \
                <div style="font-size:8px;line-height:8px;color:#C0C0C0; \
                text-align:right;">click to edit</div>'
                .replace('_text', textToHtml(outer.getCellCache($(this))));
        },
        popover_title: function() {
            return outer.attrAt(outer.cellIndex($(this))).name;
        },
        overflow: function(ele) {
            //return (ele.text() > maxWidth || ele.text.indexOf('\n') >= 0);
            return (ele[0].offsetWidth < ele[0].scrollWidth || ele.text().indexOf('\n') >= 0);
            //return (ele.prop('scrollWidth') > ele.innerWidth() || ele.text().indexOf('\n') >= 0)
        },
        editable: function(ele) {
            var index = outer.cellIndex(ele);

            //if(index[1] >= outer.schema.length) return false; // not in table
            var attr = outer.attrAt(index);
            if(attr.primaryKey) return false;
            else
                return true;
        },
    };
    this.setData(data);
    //this.updateResultVerbose();
}

ResultTable.prototype = {
    buildSchema: function(schema, self) {
        var outer = this;
        $.each(schema, function(key, value) {
            value.parent = self;
            if(value.children == undefined)
                value.children = [];
            else
                outer.buildSchema(value.children, value);
        });
    },
    
    setData: function(data, copyData) {
        // model
        this.data = [[]].concat(copyData ? deepCopy(data) : data);
        // view
        this.resetContent();
    },
    
    // table access
    cellIndex: function(cell) { // index of a cell in result table
        /*var pos = cellPosition(cell);
        var index = [];
        cell = cell.closest('[rtLevel]');
        while(cell.length) {
            index.unshift(cell.attr('rtIndex'));
            cell = this.cellParent(cell);
        }
        return [pos.row].concat(index);*/
        return cell.data('rtIndex');
    },
    
    attrAt: function(index) { // index starting from rowId

        var attr = this.schema[index[1]]; // start from rowId
        for(var i = 2; i < index.length; i++) { // skip rowId and colId
            //if(!attr.children) return undefined;
            attr = attr.children[index[i]];
            //if(!attr) return undefined;
        }
        return attr;
    },
    
    getRow: function(rowId) {
        return this.$table.find('tr:eq(' + rowId + ')');
    },
    
    getRowCnt: function() {
        return this.$table.find('tr').length;
    },
    
    getCell: function(row, col) {
        return this.$table.find('tr:eq(' + row + ') td:eq(' + col + ')');
    },
    
    
    // callback util
    callback: function(ele, funcname) { // get callback function inherited on defined on the element
        var index = this.cellIndex(ele);
        var attr = this.attrAt(index);
        var func = undefined;
        while(attr && ((funcmap = attr.callback) ? !(func = attr.callback[funcname]) : true)) {
            attr = attr.parent;
        }
        return func ? func : this.defaultCallback[funcname];
    },
    
    addCallback: function(index, funcname, func) {
        var attr = this.attrAt(index);
        if(!attr.callback)
            attr.callback = {};
        attr.callback[funcname] = func;
    },
    
    // callback wrapper
    edit: function(cell) { // wrapper for edit callback
        var children = this.cellChildren(cell);
        if(children.length != 0) { // not leaf
            var editable = true;
            for(var i = 0; i < children.length; i++) {
                if(!this.editable(children[i])) {
                    editable = false;
                    break;
                }
            }
            if(editable)
                return this.callback(cell, 'editNonLeaf')(cell);
            else
                return cell;
        } else { // leaf
            if(!this.editable(cell) || (cell.data('overflow') && this.popoverEnabled(cell)))
                return cell; // if not editable or there is popover
            var obj = (cell.data('cache') ? cell.data('cache') : arrayAt(this.data, this.cellIndex(cell)));
            return this.callback(cell, 'editLeaf')(cell, obj);
        }
    },
    
    view: function(cell) {
        if(this.cellChildren(cell).length != 0) { // not leaf
            this.callback(cell, 'viewNonLeaf')(cell);
        } else {
            var obj = (cell.data('cache') ? cell.data('cache') : arrayAt(this.data, this.cellIndex(cell)));
            this.callback(cell, 'viewLeaf')(cell, obj);
        }
        
        if(this.popoverEnabled(cell)) {
            var of = this.overflow(cell);
            if(!cell.data('overflow') && of)  {
                cell.data('overflow', true);
                this.addPopover(cell);
            } else if(cell.data('overflow') && !of) {
                cell.data('overflow', false);
                cell.popoverex('destroy');
            }
        }
        return cell;
    },
    
    editable: function(cell) {
        return this.callback(cell, 'editable')(cell);
    },
    
    overflow: function(cell) {
        return this.callback(cell, 'overflow')(cell);
    },
    
    // row manipulator
    newRow: function(rowId) {
        // we are able to build a new row before adding it to the table
        // because we assume that rowId is useless when building a row
        var row = $('<tr></tr>');
        for(var i = 0; i < this.schema.length; i++) {
            var col = $('<td class="cell" rtLevel="1"></td>');
            col.data('rtIndex',[rowId, i]);
            row.append(col);
            this.createCell(col);
        }
        row.append('<td><div> \
            <button class="btn btn-icon"><i class="icon-ok"></i></button> \
            <button class="btn btn-icon"><i class="icon-remove"></i></button> \
            <button class="btn btn-icon"><i class="icon-repeat"></i></button> \
            </div></td>');
        return row;
    },
    
    pushRow: function(rowData) { //TODO: animation
        // model
        this.data.push(deepCopy(rowData));
        // view
        var newrowId = this.getRowCnt();
        this.$table.find('tbody').append(this.newRow(newrowId));
        this.updateRowView(newrowId);
        //this.updateResultVerbose();
    },
    
    removeRow: function(rowid) { //TODO: animation
        // model
        //TODO: use lazy removal to speedup
        this.data.splice(rowid, 1);
        // view
        this.getRow(rowid).remove(); //TODO: any uncleaned data? popover events?
        //this.updateResultVerbose();
    },
    
    popRow: function() {
        this.removeRow(this.getRowCnt() - 1);
    },
    
    resetRow: function(rowId) {
        this.removeRowCache(rowId);
        this.updateRowView(rowId);
        this.getRow(rowId).removeClass();
    },
    
    commitRow: function(rowId) { // write from buffer to data
        var row = this.getRow(rowId);
        var children = row.children();
        for(var i = 0; i < this.schema.length; i++) {
            this.data[rowId][i] = deepCopy(this.getCellCache($(children[i])));
        }
        row.removeClass().addClass('success');
        setTimeout(function() { row.removeClass(); }, 3000);
    },
    
    checkRow: function(rowId) {
        var children = this.getRow(rowId).children();
        for(var i = 0; i < this.schema.length; i++) {
            if(!this.checkCell($(children[i]))) return false;
        }
        return true;
    },
    
    resetContent: function() {
        var curRowCnt = this.getRowCnt();
        var minRowCnt = Math.min(curRowCnt, this.data.length);
        // skip header
        for(var rowId = 1; rowId < minRowCnt; rowId++) {
            this.resetRow(rowId);
        }
        if(curRowCnt > this.data.length) {
            for(var t = curRowCnt - this.data.length; t--; ) {
                this.$table.find('tr:last').remove();
            }
        } else if(curRowCnt < this.data.length) {
            var tbody = this.$table.find('tbody');
            for(var t = curRowCnt; t < this.data.length; t++) {
                tbody.append(this.newRow(t));
                this.updateRowView(t);
            }
        }
    },
    
    // display current cached data
    updateRowView: function(rowId) {
        var row = this.getRow(rowId);
        for(var i = 0; i < this.schema.length; i++) {
            var cell = $(row.children()[i]);
            this.view(cell);
        }
    },
    
    addPopover: function(div) {
        //TODO: maybe not textarea
        var outer = this;
        div.popoverex({
            trigger: 'hover',
            hoverReserve: "in in_popover",
            delay: {show: 100, hide: 1000},
            placement: 'bottom',
            html: true,
            title: outer.callback(div, 'popover_title'),
            container: 'body',
            content: outer.callback(div, 'popover_content'),
            popover_click: function(e) {
                if($(e.target).prop('tagName') == 'DIV') 
                    outer.callback(div, 'popover_edit')(e.data.ele, e.data.pop);
            },
        });
    },
    
    // cache related
    buildCellCache: function(cell) {
        var children = this.cellChildren(cell);
        if(children.length != 0) {
            $.each(children, function(key, value) {
                this.buildCellCache($(value));
                cell.data('cache').data.push($(value).data('cache'));
            });
        }
        return cell;
    },
    
    setCellCache: function(cell, obj) {
        var outer = this;
        var children = this.cellChildren(cell);
        if(children.length == 0) {
            if(obj == undefined) return cell;
            if(typeof obj != 'object' && typeof obj != 'string') // non-string primitive typeof
                obj += ''; // convert to string
            cell.data('cache', deepCopy(obj));
        }
        else {
            if(!isArray(obj) || obj.length == 0) return cell;
            $.each(children, function(key, value) {
                outer.setCellCache($(value), obj[key]);
            });
        }
        return cell;
    },
    
    // get cached data, real data is returned if there is not
    getCellCache: function(cell) { 
        var outer = this;
        var children = this.cellChildren(cell);
        if(children.length == 0) {
            return cell.data('cache') ? cell.data('cache') : arrayAt(this.data, this.cellIndex(cell));
        }
        else {
            var ret = [];
            $.each(children, function(key, value) {
                ret.push(outer.getCellCache($(value)));
            });
            return ret;
        }
    },
    
    removeCellCache: function(cell) {
        var outer = this;
        var children = this.cellChildren(cell);
        if(children.length == 0)
            cell.removeData('cache');
        else {
            $.each(children, function(key, value) {
                outer.removeCellCache($(value));
            });
        }
        return cell;
    },
    
    removeRowCache: function(rowId) {
        var row = this.getRow(rowId);
        var children = row.children();
        for(var i = 0; i < this.schema.length; i++) {
            this.removeCellCache($(children[i]));
        }
    },
    
    // cell manipulator
    cellChildren: function(cell) {
        return cell.data('rtChildren');
        //return cell.find('[rtLevel=' + (parseInt(cell.attr('rtLevel')) + 1) + ']');
    },
    
    cellParent: function(cell) {
        return cell.parents('[rtLevel="' + (parseInt(cell.attr('rtLevel')) - 1) + '"]');
    },
    
    setCell: function(cell, obj) {
        this.setCellCache(cell, obj);
        //cell.data('cache', deepCopy(obj));
        this.view(cell);
    },
    
    modifyCell: function(cell, obj) { // param obj is used when data src is from popover etc.
        var pos = cellPosition(cell);
        obj = (obj != undefined ? obj : this.callback(cell, 'cellDataFromEdit')(cell));
        var cache = this.getCellCache(cell);

        if(deepCmp(cache, obj) != 0) {
            this.setCell(cell, obj);
            if(this.checkRow(pos.row)) {
                this.getRow(pos.row).removeClass().addClass('warning');
            } else {
                this.getRow(pos.row).removeClass().addClass('error');
            }
        } else {
            this.view(cell);
        }
    },
    
    checkCell: function(cell, attr) { // use attr as parameter in order to speed up the recursion
        attr = attr ? attr : this.attrAt(this.cellIndex(cell));
        var children = this.cellChildren(cell);
        
        if(children.length == 0) {
            if(!checkType(this.getCellCache(cell), attr.type)) return false;
        } else {
            for(var i = 0; i < children.length; i++) {
                var child = $(children[i]);
                if(!this.checkCell(child, attr[i])) return false;
            }
        }
        return true;
    },
    
    createCell: function(cell) { // assumes that the cell structure never changes
        var curLevel = parseInt(cell.attr('rtLevel')), curIndex = this.cellIndex(cell);

        var attr = this.attrAt(curIndex);
        
        if(attr.children.length == 0) cell.addClass('text-cropped');
        cell.html('');
        var subCellArr = [];
        for(var i = 0; i < attr.children.length; i++) {
            var subCell = $('<div class="cell cell-content" rtLevel="' + (curLevel + 1) + '"></div>');
            subCell.data('rtIndex', curIndex.concat([i]));
            cell.append(subCell);
            this.createCell(subCell);
            subCellArr.push(subCell);
        }
        cell.data('rtChildren', subCellArr);
    },
    
    // popover related
    popoverEnabled: function(cell) {
        var attr = this.attrAt(this.cellIndex(cell));
        if(!attr.popover) return false;
        for(var curAttr = attr.parent; curAttr; curAttr = curAttr.parent) {
            if(curAttr.popover) return false;
        }
        return true;
    },
}