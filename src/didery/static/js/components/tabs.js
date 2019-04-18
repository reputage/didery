let tables = require("./tables");
let tabled_tab = require("./tabledtab");

module.exports = {
    ErrorsTab: class Errors extends tabled_tab.TabledTab{
        constructor() {
            super();
            this.Name = "Errors";
            this.Icon = "i.exclamation.circle.icon";
            this.DataTab = "errors";
            this.Active = false;

            this._menu_attrs = {"data-tab": this.DataTab};
            this._tab_attrs = {"data-tab": this.DataTab};

            if (this.Active) {
                this._menu += ".active";
                this._tab += ".active";
            }

            this._detailsId = this.DataTab + "DetailsCodeBlock";
            this._copiedId = this.DataTab + "CopiedCodeBlock";
            this._copyButtonId = this.DataTab + "CopyButton";
            this._clearButtonId = this.DataTab + "ClearButton";
        }

        setup_table () {
            this.table = new tables.ErrorsTable();
        }
    },

    RelaysTab: class Relays extends tabled_tab.TabledTab{
        constructor() {
            super();
            this.Name = "Relays";
            this.Icon = "i.server.icon";
            this.DataTab = "relays";
            this.Active = false;

            this._menu_attrs = {"data-tab": this.DataTab};
            this._tab_attrs = {"data-tab": this.DataTab};

            if (this.Active) {
                this._menu += ".active";
                this._tab += ".active";
            }

            this._detailsId = this.DataTab + "DetailsCodeBlock";
            this._copiedId = this.DataTab + "CopiedCodeBlock";
            this._copyButtonId = this.DataTab + "CopyButton";
            this._clearButtonId = this.DataTab + "ClearButton";
        }

        setup_table () {
            this.table = new tables.RelaysTable();
        }
    },

    BlobsTab: class Blobs extends tabled_tab.TabledTab{
        constructor() {
            super();
            this.Name = "Encrypted Blobs";
            this.Icon = "i.unlock.alternate.icon";
            this.DataTab = "blobs";
            this.Active = false;

            this._menu_attrs = {"data-tab": this.DataTab};
            this._tab_attrs = {"data-tab": this.DataTab};

            if (this.Active) {
                this._menu += ".active";
                this._tab += ".active";
            }

            this._detailsId = this.DataTab + "DetailsCodeBlock";
            this._copiedId = this.DataTab + "CopiedCodeBlock";
            this._copyButtonId = this.DataTab + "CopyButton";
            this._clearButtonId = this.DataTab + "ClearButton";
        }

        setup_table () {
            this.table = new tables.BlobsTable();
        }
    },

    HistoryTab: class History extends tabled_tab.TabledTab{
        constructor() {
            super();
            this.Name = "Public Keys";
            this.Icon = "i.key.icon";
            this.DataTab = "history";
            this.Active = true;

            this._menu_attrs = {"data-tab": this.DataTab};
            this._tab_attrs = {"data-tab": this.DataTab};

            if (this.Active) {
                this._menu += ".active";
                this._tab += ".active";
            }

            this._detailsId = this.DataTab + "DetailsCodeBlock";
            this._copiedId = this.DataTab + "CopiedCodeBlock";
            this._copyButtonId = this.DataTab + "CopyButton";
            this._clearButtonId = this.DataTab + "ClearButton";
        }

        setup_table () {
            this.table = new tables.HistoryTable();
        }
    }
};