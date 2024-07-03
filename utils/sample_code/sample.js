function require(script) {
    $.ajax({
        url: script,
        dataType: "script",
        async: false,           // <-- this is the key
        success: function () {
            // all good...
        },
        error: function () {
            throw new Error("Could not load script " + script);
        }
    });
}
function includeCSS(stylesheet) {
    var head = $("head")[0];

    for (var i = 0; i < head.children.length; i++) {
        if (head.children[i].href != undefined && head.children[i].href == stylesheet) {
            return;
        }
    }

    $("head").append("<link href='" + stylesheet + "' type='text/css' rel='stylesheet' />");
}

//add required scripts for slickgrid
require("/SlickGrid/core/lib/jquery.event.drag-2.0.min.js");
require("/SlickGrid/core/slick.core.js");
require("/SlickGrid/core/slick.grid.js");
require("/SlickGrid/core/slick.dataview.js");
require("/Scripts/jquery.slickgrid.toolbar.js");
require("/Scripts/jquery.slickgrid.footer.js");

//add plugin scripts for slickgrid
require("/SlickGrid/core/plugins/slick.rowselectionmodel.js");
require("/SlickGrid/core/plugins/slick.checkboxselectcolumn.js");
require("/SlickGrid/core/plugins/slick.cellselectionmodel.js");
require("/SlickGrid/core/plugins/slick.cellrangeselector.js");
require("/SlickGrid/core/plugins/slick.cellrangedecorator.js");
require("/SlickGrid/core/plugins/slick.cellcopymanager.js");
require("/Scripts/jquery.slickgrid.plugins.js");

//add required css files for slickgrid
includeCSS("/SlickGrid/core/slick.grid.css");
includeCSS("/Styles/jquery.slickgrid.css");

//add base formatters for slickgrid
require("/Scripts/jquery.slickgrid.coreformatters.js");

(function ($, undefined) {

    var slickgridID = 0;
    var $doc = $(document);

    $.widget(".slickgrid", {
        
        // default options
        options: {
            gridName: "",
            gridTitle: "",
            showHeader: true,
            showFooter: true,
            gridHeight: 500,
            gridWidth: 800,
            dataField: "",
            defaultColumns: {},
            columns: {},
            editors: "",
            formatters: "",
            plugins: "",
            includeCheckboxColumn: true,
            checkDisabledCheckbox: true,
            includeExceptionColumn: true,
            usePaging: false,
            useAllPagingSort: false,
            useAllPagingSortFunc: "",
            recordsPerPage: 250,
            locked: false,
            enableNewRow: true,
            onSingleClick: "",
            onDoubleClick: "",
            onAfterGetUserSettings: null,
            onBeforeSaveUserSettings: null,
            onAfterSaveUserSettings: null,
            hideDeletedRecords: true,
            defaultSortOrder: "",
            gridTypeID: 0,
            frozenColumn: -1,
            bypassDefaultColumns: true,
            bypassDirtyCheck: false,
            rowHeight: 24
        },

        _create: function () {
            var el = this.element.hide();
            var o = this.options;
            var d;
            var cols = new Array();
            var defcols = new Array();
            var gridSettingCols = "";
            var data;
            var hiddenIDCol = "";

            //include formatter script files
            if (o.formatters != "") {
                require("/SlickGrid/core/slick.formatters.js");
                require(o.formatters);
            }
            //include editor script files
            if (o.editors != "") {
                require("/SlickGrid/core/slick.editors.js");
                require(o.editors);
            }

            if (o.dataField == "" || o.dataField == undefined) {
                d = $("#hdnData").val();
            } else {
                d = $("#" + o.dataField).val();
            }

            if (d != undefined) {
                if (d != "") {
                    data = JSON.parse(d);
                } else {
                    data = d;
                }

                if (o.columns.length == undefined) {
                    for (var key in data[0]) {
                        if (data[0].hasOwnProperty(key)) {
                            cols.push(new slickGridColumn(key, key, key));
                        }
                    }
                } else {
                    cols = JSON.parse(o.columns);
                    if (o.includeCheckboxColumn === true) {
                        checkboxSelector = (this.checkboxSelector = new CTG.Slick.CheckboxSelectColumn({
                            cssClass: "slick-cell-checkboxsel", dataView: "dataView" }));
                        cols.unshift(checkboxSelector.getColumnDefinition());
                        this.options.frozenColumn++;
                    }
                    if (o.includeExceptionColumn === true) {
                        cols.unshift(new slickGridColumn("exception", "", "Exception", CTG.Slick.Formatters.Exception, "", 30, false, false, false, false, false, false, "slick-cell-checkboxsel"));
                        this.options.frozenColumn++;
                    }

                    for (var i = 0; i < cols.length; i++) {
                        var col = cols[i];

                        if (typeof col.formatter === "string" && col.formatter !== "") {
                            col.formatter = eval(col.formatter);
                        }

                        if (typeof col.editor === "string" && col.editor !== "") {
                            col.editor = eval(col.editor);
                        }
                    }
                }
                if (o.defaultColumns.length == undefined) {
                    for (var i = 0; i < cols.length; i++) {
                        if (cols[i].id !== "exception" && cols[i].id !== "_checkbox_selector") {
                            defcols.push(cols[i].field);
                        }
                    }
                } else {
                    defcols = o.defaultColumns.split(",");
                }
                if (o.defaultSortOrder === "" && o.columns.length === undefined) {
                    for (var i = 0; i < defcols.length; i++) {
                        if (o.defaultSortOrder.length > 0) {
                            o.defaultSortOrder += ";";
                        }
                        o.defaultSortOrder += defcols[i];
                    }
                }

                for (var key in data[0]) {
                    if (data[0].hasOwnProperty(key)) {
                        if (key.toUpperCase().indexOf("HIDDEN_ID") >= 0) {
                            hiddenIDCol = key;
                            break;
                        }
                    }
                }
                if (hiddenIDCol === "") {
                    cols.push(new slickGridColumn("HIDDEN_ID", "HIDDEN_ID", "HIDDEN_ID", "", "", 0, false, false, false, false, true, false));
                    hiddenIDCol = "HIDDEN_ID";
                }

                /*var cols = new Array();
    
                for (var key in data[0]) {
                    if (data[0].hasOwnProperty(key)) {
                        cols.push(new slickGridColumn(key,key,key));
                    } 
                }*/
            } else {
                data = "";
            }

            //set grid name equal to name of container if one is not provided
            if (o.gridName == "") {
                o.gridName = el[0].id;
            }  

            this._namespaceID = this.eventNamespace || ('slickgrid_' + o.gridName);

            addnewid = (this.addnewid = -1);

            dataView = (this.dataView = new Slick.Data.DataView({ inlineFilters: false }));

            slickgrid = (this.slickgrid);

            griddata = (this.griddata = data);

            columns = (this.columns = cols);

            defcols = (this.defcols = defcols);

            defaultColumns = (this.defaultColumns = defcols);

            userColumns = (this.userColumns = "");

            gridoptions = (this.gridoptions = ({ enableCellNavigation: true, asyncEditorLoading: false, autoEdit: true, enableColumnReorder: false, frozenColumn: this.options.frozenColumn, multiColumnSort: true, rowHeight: this.options.rowHeight }));

            elementID = (this.elementID = (el[0].id));

            hiddenIDColumn = (this.hiddenIDColumn = hiddenIDCol);

            var container = (this.container = $('<div class="gridContainer" id="gridContainer_' + o.gridName + '"></div>'))
            .insertAfter(el),

            header = (this.header = $('<div class="grid-header" id="gridHeaderContainer_' + o.gridName + '"><label class="gridTitle" id="gridTitle_' + o.gridName + '">' + o.gridTitle + '</label></div>'))
            .appendTo(container),

            grid = (this.grid = $('<div id="' + o.gridName + '" class="grid"></div>'))
            .appendTo(container),

            footer = (this.footer = $('<div class="grid-footer" id="gridFooterContainer_' + o.gridName + '" > </div>'))
            .appendTo(container),

            dataRequestMask = (this.dataRequestMask = $('<div id="slickGridDataRequestMask_' + o.gridName + '" class="slickGridDataRequestMask"><div id="slickGridBusy_' + o.gridName + '" class="slickGridBusy"><span class="slickGridBusyLoader" /></div></div>'))
            .appendTo(container),

            userGridSettings = (this.userGridSettings = $('<input type="hidden" id="hdnUserGridSettings_' + o.gridName + '" />'))
            .appendTo(container),

            selections = (this.selections = $('<input type="hidden" id="hdnSelections_' + o.gridName + '" />'))
            .appendTo(container)

            selectedRowIndex = (this.selectedRowIndex = $('<input type="hidden" id="hdnSelectedRowIndex_' + o.gridName + '" />'))
            .appendTo(container)

            gridLoaded = (this.gridLoaded = false);

            if ($('#slickGridMask_' + o.gridName)[0] === undefined) {
                $('<div id="slickGridMask_' + o.gridName + '" class="slickGridMask"></div>').appendTo($(container));
            }
        },
        setWidth: function () {
            var o = this.options;

            this.container.outerWidth(o.gridWidth);
            this.grid.outerWidth(o.gridWidth);
        },
        setHeight: function () {
            var o = this.options;
            var gridHeight = o.gridHeight;

            if (o.showHeader == true) {
                gridHeight = gridHeight - 25;
            }

            if (o.showFooter == true) {
                gridHeight = gridHeight - 25;
            }

            this.container.height(o.gridHeight);
            this.grid.height(gridHeight);
        },
        _init: function () {           

            if (this.options.showHeader === false) {
                this.header.hide();
            }
            if (this.options.showFooter === false) {
                this.footer.hide();
            }

            this.setWidth();
            this.setHeight();

            //initialize grid
            this.slickgrid = new Slick.Grid(this.grid, this.dataView, this.columns, this.gridoptions);
            this.slickgrid.setSelectionModel(new Slick.RowSelectionModel({ selectActiveRow: false }));

            if (this.checkboxSelector !== undefined) {
                this.slickgrid.registerPlugin(this.checkboxSelector, this.options.gridName);
            }

            if (this.options.locked === true) {
                this.lock();
            } else {
                this.unlock();
            }

            if (this.options.enableNewRow === true) {
                this.slickgrid.setOptions({ enableAddRow: true });
            } else {
                this.slickgrid.setOptions({ enableAddRow: false });
            }

            this.slickgrid.setOptions({ enableCellNavigation: true });

            //cell click events
            if (this.options.onDoubleClick != "") {
                eval('this.slickgrid.onDblClick.subscribe(function (e, args) {' + this.options.onDoubleClick + '; })');
            }

            if (this.options.onSingleClick != "") {
                eval('this.slickgrid.onClick.subscribe(function (e, args) {' + 
                        'var item = $("#' + this.elementID + '").slickgrid("selectItem", args); ' +
                         this.options.onSingleClick + '; })');
            } else {
                eval('this.slickgrid.onClick.subscribe(function (e, args) {' +
                        'var item = $("#' + this.elementID + '").slickgrid("selectItem", args); })');
            }

            //error validation
            this.slickgrid.onValidationError.subscribe(function (e, args) {
                showStandardDialogsModal(args.validationResults.msg);
            });

            //sorting
            if (!this.options.useAllPagingSort)
                eval('this.slickgrid.onSort.subscribe(function (e, args) { $("#' + this.elementID + '").slickgrid("sort", args); })');
            else
                eval('this.slickgrid.onSort.subscribe(function (e, args) { ' + this.options.useAllPagingSortFunc + '(args); })')

            //wire up grid events
            eval('this.slickgrid.onActiveCellChanged.subscribe(function () { $("#' + this.elementID + '").slickgrid("highlightActiveRow"); })');

            eval('this.slickgrid.onCellChange.subscribe(function (e, args) { $("#' + this.elementID + '").data("slickgrid").dataView.updateItem(args.item.DataIndex, args.item); })');

            eval('this.slickgrid.onBeforeCellEditorDestroy.subscribe(function (e, args) { $("#' + this.elementID + '").slickgrid("cellEdited", e); })');

            eval('this.dataView.onRowCountChanged.subscribe(function (e, args) { $("#' + this.elementID + '").slickgrid("updateRowCount"); })');

            eval('this.dataView.onRowsChanged.subscribe(function (e, args) { $("#' + this.elementID + '").slickgrid("invalidateRows", args.rows); })');

            eval('this.slickgrid.onAddNewRow.subscribe(function (e, args) { $("#' + this.elementID + '").data("slickgrid").addNewRow(args); })');

            $(this.grid).show();

            //add dataIndex column to griddata so we can use a dataview
            var dataIndex = 0;
            var colDataIndexExists = false;
            for (var key in this.griddata[0]) {
                if (this.griddata[0].hasOwnProperty(key)) {
                    if (key.toUpperCase() == "DATAINDEX") {
                        colDataIndexExists = true;
                        break;
                    }
                }
            }
            if (colDataIndexExists === false) {
                for (var i = 0; i < this.griddata.length; i++) {
                    this.griddata[i]["DataIndex"] = dataIndex;
                    dataIndex++;
                }
            }

            //add selected and disabled columns to griddata if we are using checkboxes
            var colSelectedExists = false;
            var colDisabledExists = false;
            var colHiddenIDExists = false;

            if (this.options.includeCheckboxColumn === true) {

                //check for selected column
                for (var key in this.griddata[0]) {
                    if (this.griddata[0].hasOwnProperty(key)) {
                        if (key.toUpperCase() == "SELECTED") {
                            colSelectedExists = true;
                            break;
                        }
                    }
                }

                //check for disabled column
                for (var key in this.griddata[0]) {
                    if (this.griddata[0].hasOwnProperty(key)) {
                        if (key.toUpperCase() == "DISABLED") {
                            colDisabledExists = true;
                            break;
                        }
                    }
                }

                if (colSelectedExists === false) {
                    for (var i = 0; i < this.griddata.length; i++) {
                        this.griddata[i]["Selected"] = false;
                    }
                }



                if (colDisabledExists === false) {
                    for (var i = 0; i < this.griddata.length; i++) {
                        this.griddata[i]["Disabled"] = false;
                    }
                }
            }

            for (var key in this.griddata[0]) {
                if (this.griddata[0].hasOwnProperty(key)) {
                    if (key.toUpperCase().indexOf("HIDDEN_ID") >= 0) {
                        colHiddenIDExists = true;
                        break;
                    }
                }
            }
            if (colHiddenIDExists === false) {
                for (var i = 0; i < this.griddata.length; i++) {
                    this.griddata[i]["HIDDEN_ID"] = this.griddata[i]["DataIndex"];
                }
            }

            //Initialize dataview
            this.dataView.beginUpdate();
            this.dataView.setItems(this.griddata, "DataIndex");

            /* if (this.options.hideDeletedRecords === true) {
                 this.dataView.setFilterArgs({ deleteFlag: "true" });
                 //this.dataView.setFilter(eval('$("#' + this.options.gridName + '").slickgrid("filter");'));
                 //this.dataView.setFilter(this.filter());
             }*/

            this.dataView.endUpdate();

            //this.repaint();

            this.expandDefaultColumns();

            this.getUserGridSettings();

            this.setColumnView();

            /*highlight the first row if applicable
            if (this.griddata.length > 0) {
                try { this.slickgrid.setActiveCell(0, 0); } catch (e) { }
            }*/

            if (this.options.defaultSortOrder !== "" && this.griddata.length > 0) {
                var sortCols = this.options.defaultSortOrder.split(";");
                var args = new Array();
                var c = args.sortCols = new Array();
                var g = this.slickgrid;
                var gcols = this.slickgrid.getColumns();
                var sortName = "";

                $.each(sortCols, function () {
                    var gcs = "";
                    var parts = this.split(",");
                    var sortAsc = true;

                    sortName = parts[0];
                    if (parts.length > 1) {
                        if (parts[1] == 'ASC') {
                            sortAsc = true;
                        } else {
                            sortAsc = false;
                        }
                    }

                    var gcs = $.grep(gcols, function (m) {
                        return m.id == sortName
                    });

                    if (gcs.length !== 0) {
                        //c.push(gcs[0]);
                        var o = new Object();
                        o.sortCol = gcs[0];
                        o.sortAsc = sortAsc;
                        c.push(o);
                    }
                });

                args.grid = g;

                this.sort(args);
            }

            this.gridLoaded = true;
        },
        _toggleLock: function (unlock) {
            this.slickgrid.setOptions({ editable: unlock });
        },
        lock: function () {
            this._toggleLock(false);
            this.options.locked = true;
        },
        unlock: function () {
            this._toggleLock(true);
            this.options.locked = false;
        },
        setActiveCell: function (row, cell) {
            this.slickgrid.scrollRowIntoView(row, this.options.usePaging);
            this.slickgrid.setActiveCell(row, cell);

            var item = this.dataView.getItem(row);
            var hdnSelections = $("#hdnSelections_" + this.options.gridName).get(0);

            if (item !== undefined) {
                if (this.hiddenIDColumn !== "") {
                    hdnSelections.value = eval("item." + this.hiddenIDColumn);

                }
            }

            try {
                var hdnSelectedRowIndex = $("#hdnSelectedRowIndex_" + this.options.gridName).get(0);
                hdnSelectedRowIndex.value = row;
            }
            catch (e) { }

        },
        highlightActiveRow: function () {
            var currentCell;
            var $canvas;

            if (this.options.frozenColumn > -1)
                $canvas = $(this.slickgrid.getRightCanvasNode())
            else
                $canvas = $(this.slickgrid.getLeftCanvasNode())

            currentCell = this.slickgrid.getActiveCell();

            $canvas.find(".slick-row").removeClass("active");
            if (currentCell) {
                $canvas.find(".slick-row[row=" + currentCell.row + "]").addClass("active");
            }
        },
        updateRowCount: function (totalRecordCount, totalPageCount, pageViewNumber) {
            this.slickgrid.updateRowCount();

            //determine if we have a footer attached to this slickgrid
            var hasFooter = false;
            var footer = $('#' + this.elementID).data('slickgridfooter');

            if (footer !== undefined) {
                hasFooter = true;
            }

            //we have a footer, update the counts
            if (hasFooter == true) {
                $('#' + this.elementID).data('slickgridfooter').updateGridStatus(totalRecordCount, totalPageCount, pageViewNumber);
            }

            this.slickgrid.render();
        },
        invalidateRows: function (rows) {
            this.slickgrid.invalidateRows(rows);
            this.slickgrid.render();
        },
        addNewRow: function (args) {
            var item = args.item;
            this.addnewid = this.addnewid - 1;

            args.item["DataIndex"] = this.addnewid;

            for (var key in this.griddata[0]) {
                if (this.griddata[0].hasOwnProperty(key)) {
                    if (key.toUpperCase() !== "DATAINDEX") {
                        eval('args.item["' + key + '"] = ""');
                    }
                }
            }

            if (this.options.includeCheckboxColumn === true) {
                args.item["Selected"] = false;
                args.item["Disabled"] = false;
            }

            this.dataView.updateItem(item.DataIndex, item);
        },
        addRow: function (item) {
            //this.addnewid = this.addnewid - 1;

            //add DataItem column for dataview
            item.DataIndex = this.addnewid;

            //add hiddenid column
            if (this.hiddenIDColumn !== "") {
                eval("item." + this.hiddenIDColumn + "= " + this.addnewid);
            }

            //add checkbox related columns
            if (this.options.includeCheckboxColumn === true) {
                if (item.Selected === undefined) item.Selected = false;
                if (item.Disabled === undefined) item.Disabled = false;
            }

            /*if (this.dataView.getLength() > 0) {*/
            //add to dataview
            this.dataView.addItem(item);
            this.dataView.refresh();
            this.dataView.updateItem(item.DataIndex, item);
            /*} else { -- this was breaking deleting items, and appears to be unnecessary. (It was added to fix an issue with grids not accepting new items)
                //have to instantiate dataView since there were no records previously
                var aryData = [];
                aryData.push(item);

                this.dataView.beginUpdate();
                this.dataView.setItems(aryData, "DataIndex");
                this.dataView.endUpdate();
            }*/

            var hasFooter = false;
            var footer = $('#' + this.elementID).data('slickgridfooter');

            if (footer !== undefined) {
                hasFooter = true;
            }

            //we have a footer, update the counts
            if (hasFooter == true) {
                footer.updateGridStatus();
            }

            this.slickgrid.updateRowCount();

            //if the item is selected, run the code to see if the header checkbox should be selected as well
            if (item.Selected === true) {
                this.checkboxSelector.resetHeaderCheckBox(this.slickgrid, this.options.gridName);
            }

            this.addnewid = this.addnewid - 1;
        },
        filter: function (item, args) {
            if (this.options.hideDeletedRecords === true) {

                if (item["DeletedInd"] == args.deleteFlag) {
                    return false;
                }
            }
            return true;
        },
        sort: function (args) {
            var cols = args.sortCols;
            var grid = args.grid;

            this.dataView.sort(function (dataRow1, dataRow2) {
                for (var i = 0, l = cols.length; i < l; i++) {
                    var sortCol = cols[i].sortCol;
                    var field = cols[i].sortCol.field;
                    var sign = cols[i].sortAsc ? 1 : -1;
                    //var value1 = dataRow1[field], value2 = dataRow2[field];

                    var value1 = grid.getDataItemValueForColumn(dataRow1, sortCol);
                    var value2 = grid.getDataItemValueForColumn(dataRow2, sortCol);

                    if (isNumeric(value1) || isDecimal(value1)) {
                        value1 = prependNumericValueForSort(value1);
                    } else if (isDateForSort(value1)) {
                        value1 = formatDateForSort(value1);
                    }
                    if (isNumeric(value2) || isDecimal(value2)) {
                        value2 = prependNumericValueForSort(value2);
                    } else if (isDateForSort(value2)) {
                        value2 = formatDateForSort(value2);
                    }

                    var result = (value1 == value2 ? 0 : (value1 > value2 ? 1 : -1)) * sign;
                    if (result != 0) {
                        return result;
                    }
                }
                return 0;
            });
            this.slickgrid.invalidate();
            this.slickgrid.render();

        },
        repaint: function () {
            //determine if we have a footer attached to this slickgrid
            var hasFooter = false;
            var footer = $('#' + this.elementID).data('slickgridfooter');

            if (footer !== undefined) {
                hasFooter = true;
            }

            //we have a footer, update the counts
            if (hasFooter == true) {
                $('#' + this.elementID).slickgrid().slickgridfooter("updateGridStatus");
            }

            //run the code to see if the header checkbox should be selected as well
            if (this.options.includeCheckboxColumn === true) {
                this.checkboxSelector.resetHeaderCheckBox(this.slickgrid, this.options.gridName);
            }

            this.slickgrid.invalidate();
            this.dataView.refresh();
        },
        setColumnView: function () {
            var columns = new Array();

            if (this.userGridSettings[0].value !== "" && this.userColumns === "") {
                var gridSettings = JSON.parse(this.userGridSettings[0].value);
                var userColumnViewString = "";
                var userColumnDefinitions = new Array();
                var columns = new Array();

                $(gridSettings.Payload).find("UserColumnViewString").each(function () {
                    userColumnViewString = $(this).text();
                });

                if (userColumnViewString !== "") {
                    userColumnDefinitions = userColumnViewString.split(";");

                    for (var i = 0; i < userColumnDefinitions.length; i++) {
                        var userColumn = userColumnDefinitions[i].split(",");

                        for (var j = 0; j < this.columns.length; j++) {
                            if (userColumn[0] == this.columns[j].name && this.columns[j].name !== "") {
                                columns.push(this.columns[j]);
                                columns[columns.length - 1].width = parseInt(userColumn[1]);
                                break;
                            }
                        }
                    }

                    this.userColumns = columns;
                }
            }
            if (this.userColumns !== "" && this.options.bypassDefaultColumns === true) {
                //user user columns
                columns = this.userColumns.slice(0);
            } else {
                //set user columns to defaults
                this.userColumns = this.defaultColumns.slice(0);

                //use default columns
                columns = this.defaultColumns.slice(0);
            }

            if (this.options.includeCheckboxColumn === true) {
                checkboxSelector = (this.checkboxSelector = new CTG.Slick.CheckboxSelectColumn({ cssClass: "slick-cell-checkboxsel", dataView: "dataView" }));
                columns.unshift(checkboxSelector.getColumnDefinition());
            }

            if (this.options.includeExceptionColumn === true) {
                columns.unshift(new slickGridColumn("exception", "", "Exception", CTG.Slick.Formatters.Exception, "", 30, false, false, false, false, false, false, "slick-cell-checkboxsel"));
            }

            //apply column view to grid
            this.slickgrid.setColumns(columns);
        },
        expandDefaultColumns: function () {
            var columns = new Array();

            for (var i = 0; i < this.defaultColumns.length; i++) {
                for (var j = 0; j < this.columns.length; j++) {
                    if ((this.defcols[i] == this.columns[j].field && this.columns[j].name !== "") === true) {
                        //if ((this.defaultColumns[i] == this.columns[j].field && this.columns[j].name !== "") === true) {
                        columns.push(this.columns[j]);
                        break;
                    }
                }
            }

            this.defaultColumns = columns;
        },
        getUserGridSettings: function () {
            if (this.options.gridTypeID != 0) {

                var userid = getCookie("UserID");
                var gridName = this.options.gridName;
                var instance = this;

                $.ajax(
                    {
                        type: "POST",
                        url: '/Helpers/RestProxy.aspx/GetSlickGridSettings',
                        global: false,
                        dataType: "json",
                        contentType: "application/json",
                        async: false,
                        data: "{gridTypeID:" + this.options.gridTypeID + ", userID:" + userid + "}",
                        success: function (returnValue) {
                            var serverResponse = returnValue.d;
                            if (instance.options.onAfterGetUserSettings) {
                                serverResponse = instance.options.onAfterGetUserSettings(serverResponse);
                            }
                            $("#hdnUserGridSettings_" + gridName).val(serverResponse);
                        },
                        error: function (msg) {
                            return false;
                        }
                    }
                );
            }
        },
        selectItem: function (args) {
            var item = this.dataView.getItem(args.row);
            var hdnSelections = $("#hdnSelections_" + this.options.gridName).get(0);

            if (item !== undefined) {
                if (this.hiddenIDColumn !== "") {
                    hdnSelections.value = eval("item." + this.hiddenIDColumn);
                    /*} else {
                        hdnSelections.value = eval("item.HIDDEN_ID");*/
                }
            }
            try {
                var hdnSelectedRowIndex = $("#hdnSelectedRowIndex_" + this.options.gridName).get(0);
                hdnSelectedRowIndex.value = args.row;
            }
            catch (e) { }
        },
        updateData: function (newData) {
            var o = this.options;
            var data;

            if (newData !== "" && newData !== undefined) {
                var d = newData;
                $("#hdnData").val(newData);
            } else {
                if (o.dataField == "" || o.dataField == undefined) {
                    var d = $("#hdnData").val();
                } else {
                    var d = $("#" + o.dataField).val();
                }
            }

            if (d != undefined) {
                data = JSON.parse(d);
            } else {
                data = "";
            }

            this.griddata = data;

            //add dataIndex column to griddata so we can use a dataview
            var dataIndex = 0;
            var colDataIndexExists = false;
            for (var key in this.griddata[0]) {
                if (this.griddata[0].hasOwnProperty(key)) {
                    if (key.toUpperCase() == "DATAINDEX") {
                        colDataIndexExists = true;
                        break;
                    }
                }
            }
            if (colDataIndexExists === false) {
                for (var i = 0; i < this.griddata.length; i++) {
                    this.griddata[i]["DataIndex"] = dataIndex;
                    dataIndex++;
                }
            }

            //add selected and disabled columns to griddata if we are using checkboxes
            var colSelectedExists = false;
            var colDisabledExists = false;
            if (this.options.includeCheckboxColumn === true) {

                //check for selected column
                for (var key in this.griddata[0]) {
                    if (this.griddata[0].hasOwnProperty(key)) {
                        if (key.toUpperCase() == "SELECTED") {
                            colSelectedExists = true;
                            break;
                        }
                    }
                }

                //check for disabled column
                for (var key in this.griddata[0]) {
                    if (this.griddata[0].hasOwnProperty(key)) {
                        if (key.toUpperCase() == "DISABLED") {
                            colDisabledExists = true;
                            break;
                        }
                    }
                }

                if (colSelectedExists === false) {
                    for (var i = 0; i < this.griddata.length; i++) {
                        this.griddata[i]["Selected"] = false;
                    }
                }
                if (colDisabledExists === false) {
                    for (var i = 0; i < this.griddata.length; i++) {
                        this.griddata[i]["Disabled"] = false;
                    }
                }
            }

            for (var key in this.griddata[0]) {
                if (this.griddata[0].hasOwnProperty(key)) {
                    if (key.toUpperCase().indexOf("HIDDEN_ID") >= 0) {
                        this.hiddenIDColumn = key;
                        break;
                    }
                }
            }

            this.dataView.beginUpdate();
            this.dataView.setItems(this.griddata, "DataIndex");
            this.dataView.endUpdate();
            //this.repaint();             
            this.setColumnView();
        },
        clear: function () {
            this.griddata = new Array();
            this.dataView.beginUpdate();
            this.dataView.setItems(this.griddata, "DataIndex");
            this.dataView.endUpdate();
            //this.repaint();            
            this.setColumnView();
        },
        destroy: function () {
            this.slickgrid.destroy();
        },
        clearAlertIndicators: function () {
            var rowIndex;

            for (var dataLineItem = 0; dataLineItem < this.griddata.length; dataLineItem++) {
                var item = this.dataView.getItem(dataLineItem);
                if (typeof item != 'undefined') {
                    item.Exception = "";
                    this.dataView.updateItem(item.DataIndex, item);
                }
            }
        },
        clearAlertIndicatorByItem: function (item) {
            item.Exception = "";
            this.dataView.updateItem(item.DataIndex, item);
        },
        displayAlertIndicatorByItem: function (rowIndex, message) {
            var item = this.dataView.getItem(rowIndex);
            item.Exception = message;
            this.dataView.updateItem(item.DataIndex, item);
        },
        dataValueExists: function (field, value) {
            var foundValue = false;

            for (var i = 0; i < this.dataView.getLength() ; i++) {
                var dataItem = this.dataView.getItem(i);

                var val = eval('dataItem. ' + field);

                if (val === value) {
                    foundValue = true;
                    break;
                }
            }

            return foundValue;
        },
        disableDataRow: function (keyValuePairs) {
            var foundValue = false;

            keyValuePairs.forEach(function (row) {
                var criteria = "";

                $.each(row, function (key, value) {

                    if (criteria.length > 0)
                        criteria += ' && ';

                    criteria += "m." + key + "==" + value;

                });


                var gridItem = $.grep(this.dataView.getItems(), function (m) {
                    var result = eval(criteria);

                    return result; //eval( criteria );"m.ProductItemID == 112 && m.ProductPackageID == 112"
                });

                if (gridItem.length > 0)
                    gridItem[0].Disabled = true;

            });

            this.repaint();
            return foundValue;
        },
        disableDataViewSpecificDataRow: function (dataView, keyValuePairs) {
            var foundValue = false;

            keyValuePairs.forEach(function (row) {
                var criteria = "";

                $.each(row, function (key, value) {

                    if (criteria.length > 0)
                        criteria += ' && ';

                    criteria += "m." + key + "==" + value;

                });


                var gridItem = $.grep(dataView.getItems(), function (m) {
                    var result = eval(criteria);

                    return result; //eval( criteria );"m.ProductItemID == 112 && m.ProductPackageID == 112"
                });

                if (gridItem.length > 0)
                    gridItem[0].Disabled = true;

            });

            this.repaint();
            return foundValue;
        },
        showDataRequestMask: function () {
            var maskID = $('#slickGridDataRequestMask_' + this.options.gridName);
            var maskHeight = $(document).height();
            var maskWidth = $(window).width();
            //Set heigth and width to mask to fill up the whole screen
            $(maskID).css({ 'width': maskWidth, 'height': maskHeight });
            //transition effect		
            $(maskID).show();
            //Get the window height and width
            var winH = $(window).height();
            var winW = $(window).width();

            var id = $("#slickGridBusy_" + this.options.gridName);
            //Set the popup window to center
            $(id).css('top', winH / 2 - $(id).height() / 2);
            $(id).css('left', winW / 2 - $(id).width() / 2);
            //transition effect
            $(maskID).show();

            $('html, body').animate({ scrollTop: 0 }, 0);
        },
        hideDataRequestMask: function () {
            var maskID = $('#slickGridDataRequestMask_' + this.options.gridName);
            $(maskID).hide();
        },
        saveSearchSettings: function () {
            var hasToolbar = false;
            var toolbar = $("#" + this.elementID).data("slickgridtoolbar");

            if (toolbar !== undefined) {
                hasToolbar = true;
            }

            if (hasToolbar == true) {
                toolbar.saveColumnSettings();
            }
        },
        getSelectedItems: function () {
            return this.dataView.getSelectedItems();
        },
        clearSelectedItems: function () {
            return this.dataView.clearSelectedItems();            
        },
        getItem: function (dataIndex) {
            return this.dataView.getItemById(dataIndex);
        },
        getAllItems: function () {
            return this.dataView.getItems();
        },
        clearItems: function (items) {
            var dateIndexs = [];

            items.forEach(function (item) {
                dateIndexs.push(item.DataIndex);
            });

            dateIndexs.forEach(function (index) {
                this.dataView.deleteItem(index);
            });

            this.repaint();
        },
        scrollRowIntoView: function (row, doPaging) {            
            var rowAtTop = row * options.rowHeight;
            var rowAtBottom = (row + 1) * options.rowHeight - viewportH + (viewportHasHScroll ? scrollbarDimensions.height : 0);

            // need to page down?
            if ((row + 1) * options.rowHeight > scrollTop + viewportH + offset) {
                scrollTo(doPaging ? rowAtTop : rowAtBottom);
                render();
            }

                // or page up?
            else if (row * options.rowHeight < scrollTop + offset) {
                scrollTo(doPaging ? rowAtBottom : rowAtTop);
                render();
            }
        },
        scrollTo: function (y) {
            var oldOffset = offset;

            page = Math.min(n - 1, Math.floor(y / ph));
            offset = Math.round(page * cj);
            var newScrollTop = y - offset;

            if (offset != oldOffset) {
                var range = getVisibleRange(newScrollTop);
                cleanupRows(range.top, range.bottom);
                updateRowPositions();
            }

            var currentRow = Math.ceil(Math.abs(y / options.rowHeight));

            if (prevScrollTop != newScrollTop) {
                scrollDir = (prevScrollTop + oldOffset < newScrollTop + offset) ? 1 : -1;

                lastRenderedScrollTop = scrollTop = prevScrollTop = newScrollTop;

                var newTop = options.rowHeight * currentRow;

                if (options.frozenColumn > -1) {
                    $viewportTopR[0].scrollTop = newTop;
                }

                if (options.frozenRow > -1) {
                    $viewportBottomL[0].scrollTop = $viewportBottomR[0].scrollTop = newTop;
                }

                $viewportTopL[0].scrollTop = newScrollTop;

                trigger(self.onViewportChanged, {});
            }
        },
        cellEdited: function (e) {
            if (!this.options.bypassDirtyCheck) {
                var dirtyFlag = $("#hdnDirtyDetailPageInd").val();

                if (typeof dirtyFlag !== "undefined" && this.gridLoaded == true) {
                    SetClientSidePromptForDirtyData(true);
                }
            }
        }

    });

})(jQuery);

function slickGridColumn(id, name, field, formatter, editor, width, sortable, focusable, exportexcel, removable, hidden, showellipsedtext, cssclass, headercssclass, exportExcelAsNumberInd) {
    if (id == undefined) id = "";
    if (name == undefined) name = "";
    if (field == undefined) field = "";
    if (formatter == undefined) formatter = "";
    if (editor == undefined) editor = "";
    if (width == undefined) width = 80;
    if (sortable == undefined) sortable = false;
    if (focusable == undefined) focusable = false;
    if (exportexcel == undefined) exportexcel = false;
    if (removable == undefined) removable = false;
    if (hidden == undefined) hidden = false;
    if (showellipsedtext == undefined) showellipsedtext = false;
    if (cssclass == undefined) cssclass = "";
    if (headercssclass == undefined) headercssclass = "";
    if (exportExcelAsNumberInd == undefined) exportExcelAsNumberInd = false;

    this.id = id;
    this.name = name;
    this.field = field;

    if (formatter != "") {
        this.formatter = formatter;
    } else {
        this.formatter = formatter;
    }

    if (editor !== "") {
        this.editor = editor;
    } else {
        this.editor = editor;
    }

    this.width = width;
    this.sortable = sortable;
    this.focusable = focusable;
    this.exportexcel = exportexcel;
    this.removable = removable;
    this.hidden = hidden;
    this.showellipsedtext = showellipsedtext;
    this.cssClass = cssclass;
    this.headerCssClass = headercssclass;
    this.exportExcelAsNumberInd = exportExcelAsNumberInd;
}
function isDateForSort(val) {
    if (val == undefined) {
        return false;
    } else {
        if (isNaN(Date.parse(val))) return false;
        else return true;
    }
}
function prependNumericValueForSort(val) {
    if (val < 10)
        return "00000" + val;
    else if (val < 100)
        return "0000" + val;
    else if (val < 1000)
        return "000" + val;
    else if (val < 10000)
        return "00" + val;
    else if (val < 100000)
        return "0" + val;

    return val;
}
function formatDateForSort(val) {
    var ticks;

    var date = eval("new Date(val)");

    ticks = ((date.getTime() * 10000) + 621355968000000000);

    return ticks;
}