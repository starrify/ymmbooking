function ResultTable(data) {
    this.$table = $('#resultTable');
    this.$verbose = $('#resultVerbose');
    // model
    this.data = [schema].concat(mapResult(data));
    this.cache = deepCopyArray(this.data);
    this.overflow = createArray(data.length + 1, schema.length);
    // view
    this.updateContentView();
    this.updateResultVerbose();
}
ResultTable.prototype = {
    getRow: function(row) {
        return this.$table.find('tr:eq(' + row + ')');
    },
    
    getRowCnt: function() {
        return this.$table.find('tr').length;
    },
    
    getCell: function(row, col) {
        if(typeof row == 'number')
            return this.$table.find('tr:eq(' + row + ') td:eq(' + col + ')');
        else
            return row.find('td:eq(' + col + ')');
    },
    
    pushRow: function(rowData) { //TODO: animation
        // model
        this.overflow.push(new Array(schema.length));
        this.cache.push(deepCopyArray(rowData));
        this.data.push(deepCopyArray(rowData));
        // view
        this.$table.find('tbody').append(rowtmpl);
        this.updateRowView(this.getRowCnt() - 1);
        this.updateResultVerbose();
    },
    
    /*pushRow: function(rowData) {
        this.insertRow(rowData, this.getRowCnt().length);
    },*/
    
    removeRow: function(rowid) { //TODO: animation
        // model
        //TODO: use lazy removal to speedup
        this.overflow.splice(rowid, 1);
        this.cache.splice(rowid, 1);
        this.data.splice(rowid, 1);
        // view
        this.getRow(rowid).remove();
        this.updateResultVerbose();
    },
    
    popRow: function() {
        this.removeRow(this.getRowCnt() - 1);
    },
    
    resetRow: function(rowId) {
        // model
        this.cache[rowId] = deepCopyArray(this.data[rowId]);
        // view
        this.updateRowView(rowId);
        this.getRow(rowId).removeClass();
    },
    
    commitRow: function(rowId) { // write from buffer to data
        // model
        this.data[rowId] = deepCopyArray(this.cache[rowId]);
        // view
        var row = this.getRow(rowId);
        row.removeClass().addClass('success');
        setTimeout(function() { row.removeClass(); }, 3000);
    },
    
    updateResultVerbose: function() {
        this.$verbose.html('共有' + (this.getRowCnt() - 1) + '个搜索结果');
    },

    updateRowView: function(rowId) {
        for(var colId = 0; colId < schema.length; colId++) {
            this.setCell(this.getCell(rowId, colId), this.cache[rowId][colId]);
        }
    },
    
    updateContentView: function() {
        var curRowCnt = this.getRowCnt();

        var minRowCnt = Math.min(curRowCnt, this.data.length);
        // skip header
        for(var rowId = 1; rowId < minRowCnt; rowId++) {
            this.updateRowView(rowId);
        }
        if(curRowCnt > this.data.length) {
            for(var t = curRowCnt - this.data.length; t--; ) {
                this.$table.find('tr:last').remove();
            }
        } else if(curRowCnt < this.data.length) {
            for(var t = curRowCnt; t < this.data.length; t++) {
                this.$table.find('tbody').append(rowtmpl);
                this.updateRowView(t);
            }
        }
    },
    
    addPopover: function(param1, param2) {
        var obj;
        if(typeof param1 == 'number') { // row col
            obj = $($(this.$table.children()[param1]).children()[param2]);
        } else { // obj
            obj = param1;
        }
        
        var edit = false;
        var edittmpl = '<div><textarea style="height:100px">__texthere__</textarea></div>'
            + '<div style="text-align:center;"><button class="btn btn-primary">保存</button>'
            + '<button class="btn">放弃</button></div>';
        var viewtmpl = '<div style="word-wrap:break-word;">__texthere__</div>'
            + '<div style="font-size:8px;line-height:8px;color:#C0C0C0;text-align:right;">click to edit</div>'
        
        var self = this;
        obj.popoverex({
            trigger: 'hover', 
            hoverReserve: "in in_popover",
            delay: {show: 100, hide: 1000},
            placement: 'bottom',
            html: true,
            container: 'body',
            content: function() {
                return viewtmpl.replace('__texthere__', textToHtml($(this).text()));
            },
            popover_click: function(e) {
                if(!edit && $(e.target).prop('tagName') == 'DIV') {
                    edit = true;
                    
                    var ele = e.data.ele, pop = e.data.pop;
                    var popcontent = pop.find('[class=popover-content]');
                    ele.popoverex('pin');
                    popcontent.html(edittmpl.replace('__texthere__', ele.text())); //text()));
                    var textarea = popcontent.find('textarea');
                    textarea.focus().select();
                    
                    // register button events
                    var buttons = pop.find('button');
                    var close = function() {
                        buttons.each(function() {
                            $(this).off('click');
                        });
                        ele.popoverex('unpin');
                        ele.popoverex('hide');
                        edit = false;
                    };
                    $(buttons[0]).click(function() {
                        close();
                        self.modifyCell(ele, textarea.val())
                    });
                    $(buttons[1]).click(close);
                }
            },
        });
    },

    setCell: function(cell, text) { // with no checks
        var pos = cellPosition(cell);

        cell.html(text);
        // popover

        this.cache[pos.row][pos.col] = text;
        
        var cellOverflow = checkOverflow(cell);
        if(!this.overflow[pos.row][pos.col] && cellOverflow)  {
            this.overflow[pos.row][pos.col] = true;
            this.addPopover(cell);
        } else if(this.overflow[pos.row][pos.col] && !cellOverflow) {
            this.overflow[pos.row][pos.col] = false;
            cell.popoverex('destroy');
        }
    }, 
    modifyCell: function(param1, param2, param3) {
        var cell, pos, text, oritext;
        if(typeof param1 == 'number') { // row col
            pos.row = param1;
            pos.col = param2;
            text = param3;
            cell = this.getCell(row, col);
        } else { // cell
            cell = param1;
            text = param2;
            pos = cellPosition(cell);
        }
        //TODO: if not changed then do not set or change class
        if(this.cache[pos.row][pos.col] != text) {

            this.setCell(cell, text);
            if(isRowValid(this.getRow(pos.row))) {
                cell.closest('tr').removeClass().addClass('warning');
            } else {
                cell.closest('tr').removeClass().addClass('error');
            }
        } else {
            cell.html(text);
        }
    },
}