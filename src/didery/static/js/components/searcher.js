
module.exports = {
    searcher: {
        /*
         * Class to search for a certain string in any json object.
         */
        searchTerm: null,
        caseSensitive: false,

        setSearch: function (term) {
            /*
            * Sets search term. If term is surrounded by quotes, removes
            * them and makes search case sensitive. Otherwise, search is
            * not case sensitive.
            *
            *    Parameters::
            *    term - Base search string
            */
            this.searchTerm = term ? term : "";
            this.caseSensitive = this.searchTerm.startsWith('"') && this.searchTerm.endsWith('"');
            if (this.caseSensitive) {
                this.searchTerm = this.searchTerm.substr(1).slice(0, -1);
            } else {
                this.searchTerm = this.searchTerm.toLowerCase();
            }
        },

        _checkPrimitive: function (item) {
            /*
            * Checks for search term in provided string.
            */
            if (typeof item === "string") {
                if (!this.caseSensitive) {
                    item = item.toLowerCase();
                }
                return this.searchTerm.indexOf(item) !== -1;
            }

            return false;
        },

        _isArray: function (arr) {
            return arr.constructor.toString().indexOf("Array") > -1;
        },

        _checkAny: function (value) {
            /*
            * Checks for search term in any provided dict, list, or primitive type.
            */
            if (typeof value === "object") {
                if (!this._isArray(value)) {
                    return this.search(value);
                }

                let self = this;
                let hasSearchTerm = false;
                value.forEach(function (val, index) {
                    if (self._checkAny(val)) {
                        hasSearchTerm = true;
                    }
                });

                return hasSearchTerm;
            }

            return this._checkPrimitive(value);
        },

        search: function (obj) {
            /*
            * Returns true if obj recursively contains search term string in any field.
            */
            for (let key in obj) {
                if (obj.hasOwnProperty(key)) {
                    let value = obj[key];
                    if (this._checkAny(value)) {
                        return true;
                    }
                }
            }

            return false;
        }
    }
};