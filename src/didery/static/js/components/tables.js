let server = require("../server");
let field = require("./fields");
let m = require("mithril");

let Table = class Tables {

    constructor(fields) {
        this.no_results_text = "No results found.";

        this.max_size = 100;
        this.fields = fields;
        this.data = [];
        this._shownData = [];
        this.view = {
            "view": this._view.bind(this),
        };

        this._selected = null;
        this.detailSelected = "";

        this.filter = null;
        this.sortField = null;
        this.reversed = false;

        this.total = 0;
        this.shown = 0;
    }

    _stringify(obj) {
        /*
         * Converts provided json-like object to user-friendly string.
         *
         *   Parameters:
         *   obj - JSON like object
         */
        let replacer = function (key, value) {
            if (key.startsWith("_")) {
                return;
            }
            return value;
        };

        return JSON.stringify(obj, replacer, 2);
    }

    _limitText() {
        /*
         * Limits displayed results.
         */
        return "Limited to " + this.max_size + " results.";
    }

    _selectRow(event, obj) {
        /*
         * Deselects any previously selected row and selects row
         * specified in event.
         *
         *   Parameters:
         *   event - Specified event
         *   obj - Row data object
         */
        if (typeof this._selected !== 'undefined') {
            delete this._selected._selected;

            if (this._selected._uid === obj._uid) {
                this._selected = null;
                this.detailSelected = "";
                return;
            }
        }

        this._selected = obj;
        obj._selected = true;
        this.detailSelected = this._stringify(obj);
    }

    refresh() {
        /*
         * Refreshes data from server and returns a promise that resolves
         * when finished.
         */
        this._setData([]);
        return new Promise(function (resolve) {
            resolve();
        });
    }

    clear() {
        /*
         * Removes memory of all current data.
         */
        this.total = 0;
        server.clearArray(this.data);
    }

    _makeDummyData(count) {
        /*
         * Creates test data.
         *
         *   Parameters:
         *   count - Integer
         */
        let data = [];
        for (let i = 0; i < count; i++) {
            let obj = {};

            for (let key in this.fields) {
                if (this.fields.hasOwnProperty(key)) {
                    obj[key] = "test" + i + " " + key;
                }
            }

            data.push(obj);
        }

        return data;
    }

    _setData(data, clear = true) {
        /*
         * Clears existing data and uses provided data instead.
         * Adds "_uid" field to each piece of data, for internal tracking.
         *
         *   Parameters:
         *   data - Input data
         *   clear - Boolean
         */
        if (clear) {
            this.clear();
        }

        for (let datum in data) {
            if (data.hasOwnProperty(datum)) {
                data[datum]._uid = this.total;
                this.data.push(data[datum]);
                this.total += 1;
            }

            this._processData();

        }
    }

    setFilter(func) {
        /*
         * Sets table filter function.
         *
         *   Parameters:
         *   func - Filter function
         */
        if (func !== this.filter) {
            this.filter = func;
            this._processData();
        }
    }

    setSort(field) {
        /*
         * Sets sort on given field. If same as currently-sorted field,
         * reverse sort on said field.
         *
         *   Parameters:
         *   field - Field to sort by
         */
        if (this.sortField === field) {
            this.reversed = !this.reversed;
        } else {
            this.reversed = false;
            this.sortField = field;
        }

        this._sortData();
    }

    _sortData() {
        /*
         * Sorts table data.
         */
        if (typeof this.sortField === 'undefined') {
            return;
        }
        let self = this;
        let field = function (obj) {
            self._getField(obj, self.sortField);
        };

        this._shownData.sort(field, this.reversed);
    }

    _processData() {
        /*
         * Processes data, determines which items to show, and
         * puts items into sorted list.
         */
        server.clearArray(this._shownData);

        this.shown = 0;

        for (let i = 0; i < this.data.length; i++) {
            let obj = this.data[i];
            if (this.shown >= this.max_size) {
                break;
            }
            if (typeof this.filter !== 'undefined') {
                if (!this.filter(obj)) {
                    continue;
                }
            }

            this._shownData.push(obj);
            this.shown += 1;
        }

        this._sortData();
    }

    _getField(obj, field) {
        /*
         * Gets info from object matching given field.
         *
         *   Parameters:
         *   obj - Data object
         *   field - Field/Key
         */
        return obj[field];
    }

    _makeRow(obj) {
        /*
         * Returns array of <td> vnodes representing a row.
         *
         *   Parameters:
         *   obj - Data object
         */
        let row = [];

        for (let key in this.fields) {
            if (this.fields.hasOwnProperty(key)) {
                let field = this.fields[key].view(this._getField(obj, key));
                row.push(field);
            }
        }

        return row;
    }

    _view() {
        /*
         * Returns table markup.
         */
        let headers = [];

        for (let key in this.fields) {
            if (this.fields.hasOwnProperty(key)) {
                let header = null;
                let self = this;
                let makeScope = function (f) {
                    return function (event) {
                        self.setSort(f);
                    };
                };

                if (key === this.sortField) {
                    let icon = null;
                    if (this.reversed) {
                        icon = m("i.angle.down.icon");
                    } else {
                        icon = m("i.angle.up.icon");
                    }

                    header = m(
                        "th.ui.right.labeled.icon",
                        {"onclick": makeScope(key)},
                        icon,
                        this.fields[key].title
                    );
                } else {
                    header = m("th", {"onclick": makeScope(key)}, this.fields[key].title);
                }

                headers.push(header);
            }
        }

        let rows = [];
        for (let key in this._shownData) {
            if (this._shownData.hasOwnProperty(key)) {
                let obj = this._shownData[key];
                let row = this._makeRow(obj);
                let self = this;
                let makeScope = function (o) {
                    return function (event) {
                        self._selectRow(event, o);
                    };
                };

                if (obj._selected) {
                    rows.push(m("tr.active", {"onclick": makeScope(obj)}, row));
                } else {
                    rows.push(m("tr", {"onclick": makeScope(obj)}, row));
                }
            }
        }

        if (this.shown >= this.max_size) {
            rows.push(m("tr", m("td", this._limitText())));
        }

        if (!this.shown) {
            rows.push(m("tr", m("td", this.no_results_text)));
        }

        return m("table", {"class": "ui selectable celled unstackable single line left aligned table"},
            m("thead",
                m("tr", {"class": "center aligned"}, headers)
            ),
            m("tbody",
                rows
            )
        );
    }
};

let ErrorsTable = class Errors extends Table {
    constructor() {
        let fields = [
            new field.FillField("Title"),
            new field.FillField("Message"),
            new field.DateField("Time"),
        ];

        super(fields);
    }

    refresh() {
        /*
         * Refreshes table data.
         */
        this.clear();
        let errors = server.serverManager.errors;

        let self = this;
        return errors.refreshResource().then(function () {
            self._setData(errors.errors);
        });
    }

    static _getField(obj, field) {
        /*
         * Extracts data from json-like object.
         *
         *   Parameters:
         *   obj - Data object
         *   field - Field/Key
         */
        if (field.name === "title") {
            return obj.title;
        } else if (field.name === "message") {
            return obj.messag;
        } else if (field.name === "time") {
            return obj.time;
        }
    }
};

let RelaysTable = class Relays extends Table {
    constructor() {
        let fields = [
            new field.FillField("Host"),
            new field.FillField("Port"),
            new field.FillField("Name"),
            new field.FillField("Main"),
            new field.IDField("UID"),
            new field.FillField("Status")
        ];

        super(fields);
    }

    refresh() {
        /*
         * Refreshes table data.
         */
        this.clear();
        let relays = server.serverManager.relays;

        let self = this;
        return relays.refreshResource().then(function () {
            self._setData(relays.relays);
        });
    }

    static _getField(obj, field) {
        /*
         * Extracts data from json-like object.
         *
         *   Parameters:
         *   obj - Data object
         *   field - Field/Key
         */
        if (field.name === "host") {
            return obj["host_address"];
        } else if (field.name === "port") {
            return obj["port"];
        } else if (field.name === "name") {
            return obj["name"];
        } else if (field.name === "main") {
            return obj["main"];
        } else if (field.name === "uid") {
            return obj["uid"];
        } else if (field.name === "status") {
            return obj["status"];
        }
    }
};

let BlobsTable = class Blobs extends Table {
    constructor() {
        let fields = [
            new field.DIDField("DID"),
            new field.FillField("Blob")
        ];

        super(fields);
    }

    refresh() {
        /*
         * Refreshes table data.
         */
        this.clear();
        let otpBlobs = server.serverManager.otpBlobs;

        let self = this;
        return otpBlobs.refreshResource().then(function () {
            self._setData(otpBlobs.otpBlobs);
        });
    }

    static _getField(obj, field) {
        /*
         * Extracts data from json-like object.
         *
         *   Parameters:
         *   obj - Data object
         *   field - Field/Key
         */
        if (field.name === "did") {
            return obj.otp_data.id;
        } else if (field.name === "blob") {
            return obj.otp_data.blob;
        }
    }
};

let HistoryTable = class History extends Table {
    constructor() {
        let fields = [
            new field.DIDField("DID"),
            new field.DateField("Changed"),
            new field.FillField("Signer"),
            new field.FillField("Signers"),
            new field.FillField("Signatures")
        ];

        super(fields);
    }

    refresh() {
        /*
         * Refreshes table data.
         */
        this.clear();
        let history = server.serverManager.history;

        let self = this;
        return history.refreshResource().then(function () {
            self._setData(history.history);
        });
    }

    static _getField(obj, field) {
        /*
         * Extracts data from json-like object.
         *
         *   Parameters:
         *   obj - Data object
         *   field - Field/Key
         */
        if (field.name === "did") {
            return obj.history.id;
        } else if (field.name === "changed") {
            return obj.history.changed;
        } else if (field.name === "signer") {
            return obj.history.signer;
        } else if (field.name === "signers") {
            let signers = "";
            obj.history.signers.forEach(function (signer, index) {
                signers += signer + ", ";
            });

            return signers.slice(0, -2);
        } else if (field.name === "signatures") {
            let signatures = "";
            obj.signatures.forEach(function (sig, index) {
                signatures += sig + ", ";
            });

            return signatures.slice(0, -2);
        }
    }
};

module.exports = {
    "Table": Table,
    "ErrorsTable": ErrorsTable,
    "RelaysTable": RelaysTable,
    "BlobsTable": BlobsTable,
    "HistoryTable": HistoryTable,
};