DEFAULT_INTERVAL = 1000;


request = function (path, args) {
    /* Performs a mithril GET request.

           Parameters:
           path - Endpoint string
           args - Dictionary of path query arguments

           Returns:
           Promise from m.request
     */
    let query = "?";
    for (let key in args){
        if(args.hasOwnProperty(key)) {
            query += key + "=" + args[key] + "&";
        }
    }

    if(query.length > 1){
        path += query.slice(0, -1);
    }

    return m.request(path);
};

onlyOne = function(func, interval=1000){
    /*
    * Enforces the promise function. Never called more than once
    * per interval.
    *
    *    Parameters:
    *    func - Executor function
    *    interval - Promise interval in milliseconds
    */
    let scope = {"promise": null, "lastCalled": 0};

    return () => {
        let now = new Date();
        if(scope.promise !== null && (now - scope.lastCalled) < interval){
            return scope.promise;
        }

        scope.lastCalled = now;

        let f = function (resolve, reject) {
            let p = func();
            p.then(resolve);
            p.catch(reject);
        };

        scope.promise = new Promise(f);
        return scope.promise;
    };
};

clearArray = function (arr) {
    /*
    * Clears an array/list.
    *
    *    Parameters:
    *    a - Array/List to be cleared
    */
    while(len(arr) > 0){
        arr.pop();
    }
};


let Resource = class Res{

    constructor(path){
        Res.Refresh_Interval = DEFAULT_INTERVAL;

        this.path = path;
        this.resources = [];
        this.refreshResource = onlyOne(this._refreshResource, Res.Refresh_Interval);
    }

    _refreshResource(){
        /*
            Clears resource array and retrieves fresh data.
        */

        clearArray(this.resources);
        return request(this.path).then(this._parseAll);
    }

    _parseAll(data){
        if ('data' in data) {
            let self = this;
            data['data'].forEach(function (resource, index) {
                self.resources.push(resource);
            });
        }
    }

};

let Relays = class Rel extends Resource{

    constructor(path){
        super(path)
    }

    _parseAll(data){
        for(let key in data){
            if(data.hasOwnProperty(key)){
                this.resources.push(data[key]);
            }
        }
    }
};

serverManager = {
    errors: new Resource("/errors"),
    history: new Resource("/history"),
    otpBlobs: new Resource("/blob"),
    relays: new Relays("/relay"),
};

module.exports = {
    "request": request,
    "onlyOne": onlyOne,
    "clearArray": clearArray,
    "Resource": Resource,
    "Relays": Relays,
    "serverManager": serverManager,
};