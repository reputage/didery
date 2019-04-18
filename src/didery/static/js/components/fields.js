let m = require("mithril");

let Field = class F{

    constructor(title=null, length=null){
        /*
         * Initialize Field object. Set title and length.
         */
        F.Title = null;
        F.Length = 4;

        this.title = F.Title;
        if(title !== null){
            this.title = title;
        }

        this.mlength = F.Length;
        if(length !== null){
            this.mlength = length;
        }

        this.name = this.title.toLowerCase();
    }

    format(data){
        /*
         * Formats the data to a string matching the expected view for this field.
         *
         *   Parameters:
         *   data - Data object to be formatted
         */
        return JSON.stringify(data);
    }

    shorten(string){
        /*
         * Shortens the string to an appropriate length for display.
         *
         *   Parameters:
         *   string - String to be shortened
         */
        return string;
    }

    view(data){
        /*
         * Returns a vnode <td> suitable for display in a table.
         *
         *   Parameters:
         *   data - Data object
         */
        if(typeof data === 'undefined'){
            data = "";
        }

        let formatted = this.format(data);
        return m("td", {"title": formatted}, this.shorten(formatted))
    }
};

let FillField = class Fill extends Field{
    constructor(title=null, length=null) {
        super(title, length);
    }

    view(data) {
        Fill.Length = 100;

        let node = super.view(data);
        node.attrs["class"] = "fill-space";

        return node;
    }
};

let DateField = class Date extends Field{
    constructor(title=null, length=null) {
        super(title, length);

        Date.Length = 12;
        Date.Title = "Date";
    }
};

let EpochField = class Epoch extends DateField{
    constructor(title=null, length=null) {
        super(title, length);
    }

    format(data) {
        data = new Date(data/1000).toISOString();
        return super.format(data);
    }
};

let IDField = class ID extends Field{
    constructor(title=null, length=null) {
        super(title, length);

        ID.Length = 4;
        ID.Title = "UID";
        ID.Header = "";
    }

    format(data) {
        if(data.startsWith(ID.Header)){
            data = data.substr(len(ID.Header));
        }

        return super.format(data);
    }
};

let DIDField = class DID extends IDField{
    constructor(title=null, length=null) {
        super(title, length);

        DID.Header = "did:dad:";
        DID.Title = "DID";
    }
};

module.exports = {
    "Field": Field,
    "FillField": FillField,
    "DateField": DateField,
    "EpochField": EpochField,
    "IDField": IDField,
    "DIDField": DIDField,
};