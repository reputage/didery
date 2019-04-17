let tab = require("./tab");

module.exports = {
    TabledTab: class TTab extends tab.Tab {
        constructor() {
            super();

            this.table = null;
            this.setup_table();
            this.copiedDetails = "";
            this._detailsId = this.DataTab + "DetailsCodeBlock";
            this._copiedId = this.DataTab + "CopiedCodeBlock";
            this._copyButtonId = this.DataTab + "CopyButton";
            this._clearButtonId = this.DataTab + "ClearButton";
        }

        setup_table() {
            /*
             * Sets up table object.
             */
            this.table = new Table([]);
        }

        _copyDetails() {
            this.copiedDetails = this.table.detailSelected;
        }

        _getRows() {
            let selector = "[data-tab='" + this.DataTab + "'].tab table > tbody > tr";
            return $(selector);
        }

        _getLabel() {
            let selector = ".menu a[data-tab='" + this.DataTab + "'] .ui.label";
            return $(selector);
        }

        _clearCopy() {
            this.copiedDetails = "";
        }

        menu_item() {
            return m(this._menu, this._menu_attrs,
                m("div.menu-item-text", this.Name),
                m(this.Icon),
                m("div.ui.label.small.menu-item-number", "{0}/{1}".format(this.table.shown, this.table.total))
            );
        }

        main_view() {
            return m("div",
                m("div.table-container", m(this.table.view)),
                m("div.ui.hidden.divider"),
                m("div.ui.two.cards", {"style": "height: 45%;"},
                    m("div.ui.card",
                        m("div.content.small-header",
                            m("div.header",
                                m("span", "Details"),
                                m("span.ui.mini.right.floated.button", {
                                        "onclick": this._copyDetails,
                                        "id": this._copyButtonId
                                    },
                                    "Copy")
                            )
                        ),
                        m("pre.content.code-block", {"id": this._detailsId},
                            this.table.detailSelected
                        )
                    ),
                    m("div.ui.card",
                        m("div.content.small-header",
                            m("div.header",
                                m("span", "Copied"),
                                m("span.ui.mini.right.floated.button", {
                                        "onclick": this._clearCopy,
                                        "id": this._clearButtonId
                                    },
                                    "Clear")
                            )
                        ),
                        m("pre.content.code-block", {"id": this._copiedId},
                            this.copiedDetails
                        )
                    )
                )
            )
        }
    }
};