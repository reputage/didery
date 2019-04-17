let tables = require("./tables");
let tabled_tab = require("./tabledtab");

module.exports = {
    ErrorsTab: class Errors extends tabled_tab.TabledTab{
        constructor() {
            super();
            Errors.Name = "Errors";
            Errors.Icon = "i.exclamation.circle.icon";
            Errors.DataTab = "errors";
            Errors.Active = false;
        }

        setup_table () {
            this.table = new tables.ErrorsTable();
        }
    },

    RelaysTab: class Relays extends tabled_tab.TabledTab{
        constructor() {
            super();
            Relays.Name = "Relays";
            Relays.Icon = "i.server.icon";
            Relays.DataTab = "relays";
            Relays.Active = false;
        }

        setup_table () {
            this.table = new tables.RelaysTable();
        }
    },

    BlobsTab: class Blobs extends tabled_tab.TabledTab{
        constructor() {
            super();
            Blobs.Name = "Encrypted Blobs";
            Blobs.Icon = "i.unlock.alternate.icon";
            Blobs.DataTab = "blobs";
            Blobs.Active = false;
        }

        setup_table () {
            this.table = new tables.BlobsTable();
        }
    },

    HistoryTab: class History extends tabled_tab.TabledTab{
        constructor() {
            super();
            History.Name = "Public Keys";
            History.Icon = "i.key.icon";
            History.DataTab = "history";
            History.Active = false;
        }

        setup_table () {
            this.table = new tables.HistoryTable();
        }
    }
};